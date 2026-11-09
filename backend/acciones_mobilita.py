"""Acciones acotadas del chat. El servidor resuelve los registros y confirma el conjunto."""
from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError, model_validator
from sqlalchemy.orm import Session

import auditoria
import database
import models
import schemas
import seguridad
from tareas_servicio import normalizar, registrar_tarea, validar_cliente_tarea

router = APIRouter(prefix='/asistente', tags=['Acciones de Mobilita'])


class Operacion(BaseModel):
    model_config = {'extra': 'forbid'}
    tipo: Literal['registrar_contacto', 'actualizar_lead', 'crear_tarea', 'actualizar_tarea',
                  'asociar_propiedad', 'agendar_visita', 'reprogramar_visita', 'solicitar_archivo',
                  'crear_lead', 'corregir_nombre']
    # Referencias humanas: el modelo nunca elige IDs ni recibe acceso SQL.
    referencia: schemas.TextoCorto | None = None
    datos: dict = Field(default_factory=dict)


class Plan(BaseModel):
    model_config = {'extra': 'forbid'}
    operaciones: list[Operacion] = Field(min_length=1, max_length=5)

    @model_validator(mode='after')
    def archivo_separado(self):
        if any(o.tipo == 'solicitar_archivo' for o in self.operaciones) and len(self.operaciones) != 1:
            raise ValueError('La solicitud de archivo debe revisarse por separado.')
        if any(o.tipo == 'crear_lead' for o in self.operaciones) and len(self.operaciones) != 1:
            raise ValueError('Crear un cliente debe revisarse por separado.')
        return self


class Contacto(schemas.InteraccionCrear):
    model_config = {'extra': 'forbid'}


class CambioLead(schemas.LeadActualizar):
    model_config = {'extra': 'forbid'}


class NuevaFicha(schemas.LeadCrear):
    model_config = {'extra': 'forbid'}


class NombreCorregido(BaseModel):
    model_config = {'extra': 'forbid'}
    nombre: schemas.Nombre


class CambioTarea(BaseModel):
    model_config = {'extra': 'forbid'}
    titulo: schemas.TextoCorto = None
    descripcion: schemas.TextoLargo | None = None
    estado: schemas.EstadoTarea = None
    prioridad: schemas.Prioridad = None
    fecha_limite: date | None = None


class NuevaTarea(BaseModel):
    model_config = {'extra': 'forbid'}
    titulo: schemas.TextoCorto
    descripcion: schemas.TextoLargo | None = None
    prioridad: schemas.Prioridad = 'Media'
    fecha_limite: date | None = None


class DatosInteres(BaseModel):
    model_config = {'extra': 'forbid'}
    nivel_interes: schemas.NivelInteres = 'Medio'
    notas: schemas.TextoLargo | None = None


class Motivo(BaseModel):
    model_config = {'extra': 'forbid'}
    motivo: schemas.TextoLargo


class Horario(BaseModel):
    model_config = {'extra': 'forbid'}
    fecha_hora: datetime
    duracion_minutos: int = Field(default=60, ge=15, le=480)
    modalidad: schemas.ModalidadVisita = 'Presencial'
    punto_encuentro: schemas.TextoCorto | None = None

    @model_validator(mode='after')
    def zona(self):
        if self.fecha_hora.utcoffset() is None:
            raise ValueError('Indica fecha, hora y zona horaria de la visita.')
        self.fecha_hora = self.fecha_hora.astimezone(timezone.utc)
        return self


TIPOS = {
    'crear_lead': NuevaFicha, 'corregir_nombre': NombreCorregido,
    'registrar_contacto': Contacto, 'actualizar_lead': CambioLead,
    'crear_tarea': NuevaTarea, 'actualizar_tarea': CambioTarea,
    'asociar_propiedad': DatosInteres, 'agendar_visita': Horario,
    'reprogramar_visita': Horario, 'solicitar_archivo': Motivo,
}
ETIQUETAS = {
    'crear_lead': 'Crear lead en mi cartera', 'corregir_nombre': 'Corregir nombre del mismo cliente',
    'registrar_contacto': 'Registrar contacto', 'actualizar_lead': 'Actualizar datos del lead',
    'crear_tarea': 'Crear tarea', 'actualizar_tarea': 'Actualizar tarea',
    'asociar_propiedad': 'Asociar propiedad de interés', 'agendar_visita': 'Agendar visita',
    'reprogramar_visita': 'Reprogramar visita', 'solicitar_archivo': 'Solicitar archivo a administración',
}


def validar_plan(operaciones):
    plan = Plan(operaciones=operaciones)
    for op in plan.operaciones:
        TIPOS[op.tipo].model_validate(op.datos)
        if op.tipo == 'actualizar_lead':
            # No permite cambiar identidad, responsables, roles ni configuración.
            prohibidos = {'nombre', 'email', 'telefono', 'origen'} & op.datos.keys()
            if prohibidos:
                raise ValueError('Esos datos deben modificarse desde la ficha.')
        if op.tipo in {'actualizar_lead', 'actualizar_tarea'} and not op.datos:
            raise ValueError('Indica qué dato necesitas cambiar.')
    return plan


def unico(filas, referencia, etiqueta):
    buscado = normalizar(referencia)
    exactas = [(r, texto) for r, texto in filas if normalizar(texto) == buscado]
    coincidencias = exactas or [(r, texto) for r, texto in filas if buscado and buscado in normalizar(texto)]
    if len(coincidencias) != 1:
        opciones = coincidencias or []
        detalle = (' Opciones: ' + '; '.join(texto for _, texto in opciones[:5]) + '.') if opciones else ''
        raise HTTPException(409, f'Indica {etiqueta} con su nombre completo; no hay una coincidencia única.' + detalle)
    return coincidencias[0][0]


def referencia_detallada(filas, referencia, etiqueta, describir):
    """Mantiene títulos breves cuando son únicos y ofrece referencias distinguibles si no."""
    try:
        return unico(filas, referencia, etiqueta)
    except HTTPException:
        detalladas = [(r, describir(r, nombre)) for r, nombre in filas]
        return unico(detalladas, referencia, etiqueta)


def resolver(db, lead, plan):
    """No devuelve opciones ajenas al cliente. Los IDs se conservan en el servidor."""
    resueltos = []
    for op in plan.operaciones:
        elemento = op.model_dump()
        if op.tipo == 'corregir_nombre':
            elemento['antes'] = {'nombre': lead.nombre}
        if op.tipo == 'actualizar_tarea':
            tarea = referencia_detallada([(t, t.titulo) for t in db.query(models.Tarea).filter_by(lead_id=lead.id).all()],
                          op.referencia, 'la tarea', lambda t, nombre: f'{nombre} · {t.estado} · {t.fecha_limite or "Sin fecha"} · Tarea {t.id}')
            elemento['registro_id'] = tarea.id
            elemento['antes'] = {k: str(getattr(tarea, k)) for k in ('titulo', 'descripcion', 'estado', 'prioridad', 'fecha_limite')}
        elif op.tipo in {'asociar_propiedad', 'agendar_visita'}:
            propiedad = referencia_detallada([(p, p.titulo) for p in db.query(models.Propiedad).all()], op.referencia, 'la propiedad',
                lambda p, nombre: f'{nombre} · {p.comuna or "Sin comuna"} · {p.codigo_interno or p.direccion} · Inmueble {p.id}')
            elemento['registro_id'] = propiedad.id
            elemento['referencia'] = propiedad.titulo
        elif op.tipo == 'reprogramar_visita':
            filas = [(v, f'{db.get(models.Propiedad, v.propiedad_id).titulo} · {v.fecha_hora.isoformat()}')
                     for v in db.query(models.Visita).filter_by(lead_id=lead.id).all()
                     if v.propiedad_id and db.get(models.Propiedad, v.propiedad_id)]
            visita = unico(filas, op.referencia, 'la visita (propiedad y fecha si hay varias)')
            elemento['registro_id'] = visita.id
            elemento['referencia'] = next(texto for registro, texto in filas if registro.id == visita.id)
            elemento['antes'] = {k: str(getattr(visita, k)) for k in
                                    ('fecha_hora', 'propiedad_id', 'ejecutivo_id', 'estado', 'duracion_minutos', 'modalidad', 'punto_encuentro')}
        if op.tipo == 'actualizar_lead':
            elemento['antes'] = {k: str(getattr(lead, k)) for k in op.datos}
        elemento['etiqueta'] = ETIQUETAS[op.tipo]
        resueltos.append(elemento)
    return resueltos


def ejecutar_plan(db, usuario, lead, operaciones):
    """El llamador confirma una sola transacción: todo el plan o ningún cambio."""
    from main import _validar_disponibilidad_visita
    for op in operaciones:
        tipo, datos = op['tipo'], op['datos']
        valor = TIPOS[tipo].model_validate(datos)
        entidad, registro = auditoria.LEAD, lead
        if tipo == 'registrar_contacto':
            registro = models.Interaccion(lead_id=lead.id, **valor.model_dump())
            db.add(registro)
            entidad = auditoria.INTERACCION
        elif tipo == 'corregir_nombre':
            if lead.nombre != op['antes']['nombre']:
                raise HTTPException(409, 'El nombre del cliente cambió. Prepara otra propuesta.')
            anterior = lead.nombre
            lead.nombre = valor.nombre
            db.flush()
            auditoria.registrar(db, usuario, auditoria.ACTUALIZAR, auditoria.LEAD, lead.id,
                               'Corrigió el nombre del lead', f'Nombre anterior: {anterior}; nombre corregido: {lead.nombre}')
            continue
        elif tipo == 'actualizar_lead':
            if any(str(getattr(lead, k)) != v for k, v in op['antes'].items()):
                raise HTTPException(409, 'Los datos del lead cambiaron. Prepara otra propuesta.')
            cambios = valor.model_dump(exclude_unset=True)
            minimo = cambios.get('presupuesto_min', lead.presupuesto_min)
            maximo = cambios.get('presupuesto_max', lead.presupuesto_max)
            if minimo is not None and maximo is not None and minimo > maximo:
                raise HTTPException(422, 'El presupuesto mínimo supera el máximo.')
            for k, v in cambios.items():
                setattr(lead, k, v)
        elif tipo == 'crear_tarea':
            pendientes = db.query(models.Tarea).filter(models.Tarea.lead_id == lead.id, models.Tarea.estado != 'Completada').all()
            if any(normalizar(t.titulo) == normalizar(valor.titulo) for t in pendientes):
                raise HTTPException(409, 'Esta tarea ya existe. Abre la tarea pendiente.')
            registrar_tarea(db, schemas.TareaCrear(lead_id=lead.id, **valor.model_dump(mode='json')), usuario)
            continue
        elif tipo == 'actualizar_tarea':
            registro = db.query(models.Tarea).filter_by(id=op['registro_id'], lead_id=lead.id).with_for_update().populate_existing().first()
            if not registro or any(str(getattr(registro, k)) != v for k, v in op['antes'].items()):
                raise HTTPException(409, 'La tarea cambió. Prepara otra propuesta.')
            for k, v in valor.model_dump(exclude_unset=True).items():
                setattr(registro, k, v)
            if registro.estado != 'Completada' and any(
                normalizar(t.titulo) == normalizar(registro.titulo)
                for t in db.query(models.Tarea).filter(models.Tarea.lead_id == lead.id,
                    models.Tarea.id != registro.id, models.Tarea.estado != 'Completada').all()
            ):
                raise HTTPException(409, 'Ya hay una tarea pendiente con ese título.')
            entidad = auditoria.TAREA
        elif tipo == 'asociar_propiedad':
            if not db.get(models.Propiedad, op['registro_id']):
                raise HTTPException(409, 'La propiedad ya no existe.')
            if db.query(models.Interes).filter_by(lead_id=lead.id, propiedad_id=op['registro_id']).first():
                raise HTTPException(409, 'La propiedad ya está asociada a este lead.')
            registro = models.Interes(lead_id=lead.id, propiedad_id=op['registro_id'], **valor.model_dump())
            db.add(registro)
            entidad = auditoria.INTERES
        elif tipo in {'agendar_visita', 'reprogramar_visita'}:
            if tipo == 'agendar_visita':
                propiedad = db.get(models.Propiedad, op['registro_id'])
                if not propiedad or propiedad.estado != 'Disponible':
                    raise HTTPException(409, 'Selecciona una propiedad disponible para agendar.')
                registro = models.Visita(lead_id=lead.id, propiedad_id=propiedad.id, ejecutivo_id=usuario.id, estado='Programada')
            else:
                registro = db.query(models.Visita).filter_by(id=op['registro_id'], lead_id=lead.id).with_for_update().populate_existing().first()
                if not registro or any(str(getattr(registro, k)) != v for k, v in op['antes'].items()) or registro.estado not in {'Programada', 'Confirmada'}:
                    raise HTTPException(409, 'La visita cambió o ya no se puede reprogramar.')
                if usuario.rol != 'admin' and registro.ejecutivo_id != usuario.id:
                    raise HTTPException(403, 'Esta visita corresponde a otro ejecutivo.')
            # Bloquea la agenda del ejecutivo para serializar solicitudes simultáneas.
            db.query(models.Usuario).filter_by(id=registro.ejecutivo_id).with_for_update().first()
            _validar_disponibilidad_visita(db, registro.ejecutivo_id, valor.fecha_hora, valor.duracion_minutos, registro.estado, registro.id)
            for k, v in valor.model_dump().items():
                setattr(registro, k, v)
            db.add(registro)
            entidad = auditoria.VISITA
        else:
            if db.query(models.SolicitudArchivo).filter_by(lead_id=lead.id, estado='Pendiente').first():
                raise HTTPException(409, 'Este lead ya tiene una solicitud pendiente de administración.')
            registro = models.SolicitudArchivo(lead_id=lead.id, lead_nombre=lead.nombre, autor_id=usuario.id,
                                               autor_nombre=usuario.nombre, motivo=valor.motivo)
            db.add(registro)
            entidad = auditoria.SOLICITUD_ARCHIVO
        db.flush()
        auditoria.registrar(db, usuario, auditoria.ACTUALIZAR if tipo.startswith(('actualizar', 'reprogramar')) else auditoria.CREAR,
                           entidad, registro.id, f'{ETIQUETAS[tipo]}: {lead.nombre}',
                           str(datos))


class ConfirmarPlan(BaseModel):
    model_config = {'extra': 'forbid'}
    confirmar: Literal[True]
    paso: str | None = Field(default=None, max_length=40)


@router.post('/acciones/{propuesta_id}/confirmar')
def confirmar_acciones(propuesta_id: int, datos: ConfirmarPlan,
                       db: Session = Depends(database.obtener_db), usuario=Depends(seguridad.usuario_actual)):
    from tareas_chat import obtener_propuesta, vigente
    propuesta = obtener_propuesta(db, propuesta_id, usuario)
    if (propuesta.propuesta or {}).get('_agenda'):
        from conversacion_mobilita import confirmar_paso
        return confirmar_paso(db, usuario, propuesta, datos.paso)
    if (propuesta.propuesta or {}).get('accion') != 'gestionar':
        raise HTTPException(409, 'Esta propuesta no contiene acciones de seguimiento.')
    lead = validar_cliente_tarea(db, propuesta.propuesta['_lead_id'], usuario)
    if propuesta.estado == 'confirmada':
        return {'mensaje': 'La propuesta ya estaba guardada. No se repitieron los cambios.'}
    vigente(propuesta)
    solo_archivo = all(o['tipo'] == 'solicitar_archivo' for o in propuesta.propuesta['_operaciones'])
    if propuesta.estado != 'pendiente' or lead.archivado or (lead.estado == 'Cerrado' and not solo_archivo):
        raise HTTPException(409, 'Prepara otra propuesta para un lead activo de tu cartera.')
    try:
        ejecutar_plan(db, usuario, lead, propuesta.propuesta['_operaciones'])
        propuesta.estado = 'confirmada'
        propuesta.confirmacion = {'confirmar': True, 'lead_id': lead.id}
        db.commit()
    except Exception:
        db.rollback()
        raise
    mensaje = ('Solicitud enviada a administración. El lead no se ha archivado.' if solo_archivo
               else 'Cambios guardados.')
    return {'mensaje': mensaje}


def crear_ficha(db, usuario, datos):
    """La creación y la confirmación se guardan juntas, sin asignaciones del LLM."""
    from main import _buscar_lead_por_email
    ficha = NuevaFicha.model_validate(datos)
    if ficha.presupuesto_min is not None and ficha.presupuesto_max is not None and ficha.presupuesto_min > ficha.presupuesto_max:
        raise HTTPException(422, 'El presupuesto mínimo supera el máximo.')
    if _buscar_lead_por_email(db, ficha.email):
        raise HTTPException(409, 'Ya existe un lead con ese correo. Revisa el registro antes de crear otro.')
    lead = models.Lead(**ficha.model_dump(), ejecutivo_id=usuario.id)
    db.add(lead)
    db.flush()
    auditoria.registrar(db, usuario, auditoria.CREAR, auditoria.LEAD, lead.id,
                       f'Creó el lead {lead.nombre} desde Mobilita')
    return lead


class Decision(BaseModel):
    model_config = {'extra': 'forbid'}
    decision: Literal['Aprobada', 'Rechazada']
    motivo: schemas.TextoLargo


@router.get('/solicitudes')
def listar_solicitudes(db: Session = Depends(database.obtener_db), usuario=Depends(seguridad.usuario_actual)):
    q = db.query(models.SolicitudArchivo)
    if usuario.rol != 'admin':
        q = q.filter_by(autor_id=usuario.id)
    return [{'id': s.id, 'lead_id': s.lead_id, 'cliente': s.lead_nombre, 'autor': s.autor_nombre,
             'motivo': s.motivo, 'estado': s.estado, 'resolucion': s.resolucion,
             'fecha': s.fecha_creacion, 'resuelto_por': s.resuelto_por_nombre}
            for s in q.order_by(models.SolicitudArchivo.estado != 'Pendiente', models.SolicitudArchivo.fecha_creacion.desc()).limit(100).all()]


@router.post('/solicitudes/{solicitud_id}/resolver')
def resolver_solicitud(solicitud_id: int, datos: Decision, db: Session = Depends(database.obtener_db),
                      usuario=Depends(seguridad.usuario_actual)):
    if usuario.rol != 'admin':
        raise HTTPException(403, 'Sólo administración puede resolver solicitudes.')
    solicitud = db.query(models.SolicitudArchivo).filter_by(id=solicitud_id).with_for_update().populate_existing().first()
    if not solicitud:
        raise HTTPException(404, 'Solicitud no encontrada.')
    if solicitud.estado != 'Pendiente':
        raise HTTPException(409, 'Esta solicitud ya fue resuelta.')
    lead = db.query(models.Lead).filter_by(id=solicitud.lead_id).with_for_update().populate_existing().first()
    if datos.decision == 'Aprobada':
        if not lead:
            raise HTTPException(409, 'El lead ya no existe.')
        lead.archivado = True
        lead.estado = 'Cerrado'
        auditoria.registrar(db, usuario, auditoria.ACTUALIZAR, auditoria.LEAD, lead.id,
                           f'Archivó el lead {lead.nombre}', 'Se conserva su historial. Solicitud de archivo aprobada.')
    solicitud.estado = datos.decision
    solicitud.resolucion = datos.motivo
    solicitud.resuelto_por_id = usuario.id
    solicitud.resuelto_por_nombre = usuario.nombre
    solicitud.fecha_resolucion = datetime.now(timezone.utc)
    auditoria.registrar(db, usuario, auditoria.ACTUALIZAR, auditoria.SOLICITUD_ARCHIVO, solicitud.id,
                       f'{datos.decision}: archivo de {solicitud.lead_nombre}', datos.motivo)
    db.commit()
    return {'estado': solicitud.estado}

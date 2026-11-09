"""El modelo propone; la API resuelve clientes y confirma sólo acciones permitidas."""
from datetime import datetime, timedelta, timezone
import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, StringConstraints, ValidationError, field_validator
from sqlalchemy.orm import Session

import auditoria
import database
import ia
import models
import schemas
import seguridad
from tareas_servicio import normalizar, registrar_tarea, obtener_tarea_permitida, validar_cliente_tarea
from consultas_mobilita import Consulta, ejecutar_consulta
from acciones_mobilita import Operacion, validar_plan, resolver
from zoneinfo import ZoneInfo
from conversacion_mobilita import Bloque, crear_agenda, activar, contexto_pendiente, sustituir_actual, resumen, validar_origen

router = APIRouter(prefix='/asistente/tareas', tags=['Asistente de tareas'])


class Solicitud(BaseModel):
    model_config = {'extra': 'forbid'}
    mensaje: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=3000)]
    anterior_id: int | None = Field(default=None, gt=0, strict=True)


class Interpretacion(BaseModel):
    model_config = {'extra': 'forbid', 'strict': True}
    accion: Literal['crear_tarea', 'gestionar', 'organizar', 'aclarar', 'no_admitida', 'responder', 'fuera_de_alcance', 'consultar']
    cliente: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)] | None
    titulo: schemas.TextoCorto | None
    descripcion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3000)] | None
    aclaracion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1200)] | None
    consulta: Consulta | None = None
    operaciones: list[Operacion] | None = None
    bloques: list[Bloque] | None = Field(default=None, min_length=1, max_length=5)


FUERA_DE_ALCANCE = 'Sólo puedo ayudarte con este CRM inmobiliario. Puedes preguntarme por leads, propiedades, seguimiento o el asistente de IA.'
ACCION_NO_ADMITIDA = 'No tienes permiso para esa acción desde Mobilita. Puedes solicitar el archivo de un lead a administración, indicando el motivo. Para otros cambios permitidos, utiliza el formulario correspondiente del CRM.'

# Contexto interno de funciones existentes; no es un manual publicado ni acceso a registros.
GUIA_CRM = '''Mobilita es el asistente del CRM inmobiliario para ejecutivos y administradores.
Inicio muestra el resumen de operación. Leads contiene perfil de búsqueda, responsable,
historial de contactos, tareas, propiedades de interés, oportunidades y visitas.
En Leads se puede filtrar Todos los clientes o Mi cartera (asignados al usuario actual).
El administrador puede reasignar leads; el historial conserva los cambios de responsable.
Propiedades gestiona fichas, fotografías, precio, características, estado y disponibilidad.
Los datos de propietario y captador se reservan a administración.
Negocios muestra las oportunidades por etapa comercial. Visitas organiza las citas.
Tareas permite registrar y editar título, descripción, cliente, prioridad, estado y fecha.
El ejecutivo sólo consulta y gestiona tareas de sus leads asignados; administración puede gestionar todas.
Revisar pendientes antes de crear otra evita duplicar el seguimiento.
En la ficha del lead, la IA prepara resumen, siguiente acción, borrador de seguimiento,
preguntas para completar el perfil y notas de una llamada escrita por el ejecutivo.
Las notas sólo se registran como contacto después de revisar y confirmar el texto.
La prioridad de atención y coincidencias con propiedades usan reglas explicables, no el LLM.
Actividad y Consumo de IA son secciones exclusivas del administrador.
Mobilita prepara contactos, cambios del perfil comercial y estado, tareas, intereses y visitas
con revisión y confirmación. Sólo actúa sobre leads de la cartera para ejecutivos.
Permite solicitar el archivo (no borrado) a administración indicando el motivo.
No cambia responsables, usuarios, roles ni configuración. No envía mensajes ni consulta internet.
Puede preparar fichas nuevas con nombre y correo obligatorio, asignadas al usuario que confirma.
Corregir un nombre sólo corrige a la misma persona: no traslada contactos entre clientes.
Organiza hasta cinco solicitudes por conversación y las confirma por separado.
Puede solicitar cinco herramientas de consulta: cartera_resumen, tareas_pendientes,
tareas_vencidas, propiedades_disponibles y ejecutivos_disponibles. El backend consulta y muestra el resultado
directamente, sin enviarte esos datos. Las tareas de una cartera son las de sus leads.
Para la cartera y tareas el alcance mia es el predeterminado, incluso para un admin.
El alcance general requiere admin y una petición explícita del resumen de todo el CRM.
Propiedades disponibles corresponde al catálogo compartido, con datos comerciales.
El listado de ejecutivos activos requiere administración y muestra nombre y cantidad de leads asignados.
Para pedir quiénes son los ejecutivos usa ejecutivos_disponibles con alcance general.
Esta consulta no reasigna leads ni cambia roles. No muestra correos, contraseñas ni claves.
No recibe fichas ni listados de la base para redactar sus respuestas generales.
Para otros datos vigentes, orienta a la pantalla o ficha correspondiente.
'''


def informacion_asistente():
    """Sólo datos públicos del producto y el nombre del modelo configurado."""
    return {
        'proyecto': 'CRM inmobiliario con asistencia de IA',
        'etapa': 'MVP académico en desarrollo y validación',
        'objetivo': 'Centralizar leads, propiedades y seguimiento comercial con apoyo de IA y revisión humana.',
        'asistente': 'Mobilita es el asistente integrado, no el nombre de todo el CRM.',
        'modelo_configurado': ia.MODELO or None,
        'referencia_funcional': 'Contexto interno del sistema sobre sus funciones; no es un documento consultable desde el chat.',
    }


def contexto_conversacion(db, anterior_id, usuario):
    """Sólo recupera turnos propios del servidor; no acepta un historial del navegador."""
    turnos = []
    usados = set()
    for _ in range(6):
        if anterior_id is None or anterior_id in usados:
            break
        usados.add(anterior_id)
        anterior = db.query(models.PropuestaTareaChat).filter_by(
            id=anterior_id, usuario_id=usuario.id).first()
        if not anterior:
            raise HTTPException(404, 'Conversación no encontrada. Inicia una nueva conversación.')
        if not turnos:
            vigente(anterior)
        else:
            try:
                vigente(anterior)
            except HTTPException:
                break
        if anterior.estado == 'error':
            raise HTTPException(409, 'Ese turno no se puede retomar. Inicia una nueva conversación.')
        # Los resultados de consultas permanecen en el CRM; no viajan al proveedor
        # en el siguiente turno ni se reutilizan como si siguieran vigentes.
        texto = ('Se procesó una consulta del CRM; solicita otra para obtener datos vigentes.'
                 if (anterior.propuesta or {}).get('accion') == 'consultar'
                 else respuesta(anterior, db, usuario)['mensaje'])
        if anterior.estado == 'confirmada':
            texto = 'La solicitud ya fue confirmada y guardada. No debe repetirse sin una nueva petición explícita.'
        turnos.append({'solicitud': anterior.solicitud, 'respuesta': texto, 'estado': anterior.estado})
        anterior_id = (anterior.propuesta or {}).get('_anterior_id')
    return list(reversed(turnos))


class Confirmacion(BaseModel):
    model_config = {'extra': 'forbid'}
    lead_id: int = Field(gt=0, strict=True)
    titulo: schemas.TextoCorto
    descripcion: schemas.TextoLargo | None = None
    prioridad: schemas.Prioridad = 'Media'
    fecha_limite: str | None = None

    _fecha = field_validator('fecha_limite')(schemas._validar_fecha_iso)


def clientes_coincidentes(db, nombre, usuario):
    # Un nombre parcial puede devolver varios clientes; nunca se elige el primero.
    buscado = normalizar(nombre)
    consulta = db.query(models.Lead).filter(models.Lead.archivado.is_(False))
    if usuario.rol != 'admin':
        consulta = consulta.filter(models.Lead.ejecutivo_id == usuario.id)
    return [c for c in consulta.order_by(models.Lead.nombre, models.Lead.id).all()
            if buscado and buscado in normalizar(c.nombre)]


def vigente(propuesta):
    fecha = propuesta.fecha_creacion
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - fecha > timedelta(minutes=30):
        raise HTTPException(409, 'La propuesta venció. Prepara una nueva antes de confirmar.')


def obtener_propuesta(db, propuesta_id, usuario):
    propuesta = db.query(models.PropuestaTareaChat).filter(
        models.PropuestaTareaChat.id == propuesta_id,
        models.PropuestaTareaChat.usuario_id == usuario.id,
    ).with_for_update().populate_existing().first()
    if not propuesta:
        raise HTTPException(404, 'Propuesta no encontrada')
    return propuesta


def respuesta(propuesta, db, usuario):
    interpretacion = propuesta.propuesta or {}
    clientes = clientes_coincidentes(db, interpretacion.get('cliente'), usuario) if propuesta.estado == 'pendiente' and not interpretacion.get('_nuevo_lead') else []
    mensaje = interpretacion.get('aclaracion') or (
        'Necesito el nombre del lead y la tarea que quieres crear.'
        if propuesta.estado == 'aclarar' else 'Revisa la tarea y confirma para guardarla.'
    )
    if interpretacion.get('accion') == 'fuera_de_alcance':
        mensaje = FUERA_DE_ALCANCE
    elif interpretacion.get('accion') == 'no_admitida':
        mensaje = ACCION_NO_ADMITIDA
    if interpretacion.get('_resultado_consulta'):
        mensaje = interpretacion['_resultado_consulta']['mensaje']
    opciones = []
    if interpretacion.get('_opciones_cliente'):
        permitidos = {c['id'] for c in interpretacion['_opciones_cliente']}
        opciones = [{'id': c.id, 'nombre': c.nombre, 'estado': c.estado, 'correo': c.email}
                    for c in clientes_coincidentes(db, interpretacion.get('cliente'), usuario) if c.id in permitidos]
        if not opciones:
            mensaje = 'Las coincidencias cambiaron. Indica nuevamente el nombre del cliente de tu cartera.'
    if propuesta.estado == 'pendiente' and not interpretacion.get('_agenda'):
        if not clientes:
            mensaje = 'No encontré un lead con ese nombre. Escribe nuevamente la solicitud con su nombre registrado.'
        elif len(clientes) > 1:
            mensaje = 'Encontré varios leads. Selecciona al correcto antes de confirmar.'
    return {
        'id': propuesta.id, 'estado': propuesta.estado, 'mensaje': mensaje,
        'clientes': [{'id': c.id, 'nombre': c.nombre, 'estado': c.estado} for c in clientes],
        'titulo': interpretacion.get('titulo') or '', 'descripcion': interpretacion.get('descripcion') or '',
        'modelo': propuesta.modelo, 'costo_estimado_usd': propuesta.costo_estimado_usd,
        'tokens_entrada': propuesta.tokens_entrada, 'tokens_salida': propuesta.tokens_salida,
        'consulta': interpretacion.get('_resultado_consulta'),
        'acciones': interpretacion.get('_operaciones'),
        'cliente_acciones': interpretacion.get('_cliente_nombre'),
        'agenda': resumen(interpretacion), 'paso': interpretacion.get('_paso'),
        'opciones_cliente': opciones,
    }


@router.post('/preparar', status_code=201)
def preparar(datos: Solicitud, db: Session = Depends(database.obtener_db),
             usuario: models.Usuario = Depends(seguridad.usuario_actual)):
    anterior = obtener_propuesta(db, datos.anterior_id, usuario) if datos.anterior_id else None
    if anterior and anterior.estado == 'continuada':
        raise HTTPException(409, 'Continúa desde el último mensaje de la conversación.')
    if anterior and (anterior.propuesta or {}).get('_agenda') and anterior.estado == 'pendiente':
        raise HTTPException(409, 'Confirma o descarta el paso actual antes de preparar otra solicitud.')
    pendiente = contexto_pendiente(anterior.propuesta or {}) if anterior else None
    turnos = contexto_conversacion(db, datos.anterior_id, usuario)
    contexto = json.dumps({'guia_crm': GUIA_CRM, 'informacion_asistente': informacion_asistente(),
                          'rol_actual': usuario.rol, 'fecha_actual': datetime.now(ZoneInfo('America/Santiago')).isoformat(),
                          'turnos_anteriores': turnos, 'solicitud_actual': datos.mensaje,
                          'pendiente': pendiente}, ensure_ascii=False)
    try:
        resultado = ia.generar_analisis(contexto, 'tarea_chat')
    except ia.IANoConfigurada:
        raise HTTPException(503, 'El servicio de IA no está configurado.')
    except ia.IAFallo as error:
        raise HTTPException(502, str(error))
    propuesta = models.PropuestaTareaChat(
        usuario_id=usuario.id, solicitud=datos.mensaje, salida_original=resultado['texto'],
        modelo=resultado['modelo'], tokens_entrada=resultado['tokens_entrada'],
        tokens_salida=resultado['tokens_salida'], costo_estimado_usd=resultado['costo_estimado_usd'],
    )
    try:
        interpretacion = Interpretacion.model_validate_json(resultado['texto'])
        if interpretacion.accion == 'crear_tarea' and (
            not interpretacion.cliente or not interpretacion.titulo or
            normalizar(interpretacion.cliente) not in normalizar(' '.join(
                [t['solicitud'] for t in turnos] + [datos.mensaje]))
        ):
            raise ValueError('Cliente o tarea sin respaldo en la solicitud')
        if interpretacion.accion in {'responder', 'aclarar'} and not interpretacion.aclaracion:
            raise ValueError('Respuesta sin texto')
        if interpretacion.accion not in {'crear_tarea', 'gestionar'} and any([
            interpretacion.cliente, interpretacion.titulo, interpretacion.descripcion
        ]):
            raise ValueError('Una respuesta informativa no puede contener una tarea')
        if (interpretacion.accion == 'consultar') != (interpretacion.consulta is not None):
            raise ValueError('Herramienta ausente o fuera de una consulta')
        if (interpretacion.accion == 'gestionar') != (interpretacion.operaciones is not None):
            raise ValueError('Operaciones ausentes o fuera de una propuesta')
        if (interpretacion.accion == 'organizar') != (interpretacion.bloques is not None):
            raise ValueError('Bloques ausentes o fuera de una organización')
        propuesta.propuesta = interpretacion.model_dump()
        propuesta.propuesta['_anterior_id'] = datos.anterior_id
        agenda_estado = None
        evidencia = ' '.join([t['solicitud'] for t in turnos] + [datos.mensaje])
        if pendiente:
            evidencia += ' ' + (pendiente['solicitud_actual'].get('cliente') or '') + ' ' + (pendiente.get('cliente_elegido') or '')
            evidencia += ' ' + json.dumps(pendiente['solicitud_actual'], ensure_ascii=False)
        if interpretacion.operaciones:
            validar_origen(interpretacion.operaciones, evidencia)
        if pendiente and interpretacion.accion in {'gestionar', 'organizar', 'crear_tarea'}:
            if interpretacion.accion == 'organizar':
                if len(interpretacion.bloques) != 1:
                    raise ValueError('Completa una solicitud a la vez; las demás se conservan.')
                bloque = interpretacion.bloques[0].model_dump(mode='json')
            elif interpretacion.accion == 'crear_tarea':
                bloque = {'cliente': interpretacion.cliente, 'operaciones': [{'tipo': 'crear_tarea', 'datos': {
                    'titulo': interpretacion.titulo, 'descripcion': interpretacion.descripcion}}]}
            else:
                bloque = {'cliente': interpretacion.cliente, 'operaciones': [o.model_dump(mode='json') for o in interpretacion.operaciones]}
            crear_agenda([bloque], evidencia)  # Comprueba el origen del nombre, sin usar IDs del LLM.
            propuesta.propuesta, agenda_estado = activar(db, usuario, sustituir_actual(anterior.propuesta, bloque))
        elif interpretacion.accion == 'organizar':
            propuesta.propuesta, agenda_estado = activar(db, usuario, crear_agenda(interpretacion.bloques, evidencia))
        elif interpretacion.accion == 'gestionar':
            solicitudes = normalizar(' '.join([t['solicitud'] for t in turnos] + [datos.mensaje]))
            if not interpretacion.cliente or normalizar(interpretacion.cliente) not in solicitudes:
                raise ValueError('Cliente sin respaldo en la solicitud')
            clientes = clientes_coincidentes(db, interpretacion.cliente, usuario)
            if len(clientes) != 1 or any(o.tipo == 'crear_lead' for o in interpretacion.operaciones):
                bloque = {'cliente': interpretacion.cliente, 'operaciones': [o.model_dump(mode='json') for o in interpretacion.operaciones]}
                propuesta.propuesta, agenda_estado = activar(db, usuario, crear_agenda([bloque], evidencia))
            else:
                plan = validar_plan(interpretacion.operaciones)
                propuesta.propuesta['_operaciones'] = resolver(db, clientes[0], plan)
            if agenda_estado is not None:
                clientes = []
            if clientes:
                lead = clientes[0]
                if lead.estado == 'Cerrado' and not all(o.tipo == 'solicitar_archivo' for o in plan.operaciones):
                    raise HTTPException(409, 'El lead está cerrado. Pide a administración que revise su ficha.')
                propuesta.propuesta['_lead_id'] = lead.id
                propuesta.propuesta['_cliente_nombre'] = lead.nombre
                propuesta.propuesta['aclaracion'] = 'Revisa los cambios propuestos y confirma para guardarlos.'
        if pendiente and agenda_estado is None:
            conservado = dict(anterior.propuesta)
            conservado['aclaracion'] = (FUERA_DE_ALCANCE if interpretacion.accion == 'fuera_de_alcance'
                else ACCION_NO_ADMITIDA if interpretacion.accion == 'no_admitida'
                else interpretacion.aclaracion or 'Indica qué necesitas aclarar de esta solicitud.')
            conservado.pop('_resultado_consulta', None)
            propuesta.propuesta = conservado
            agenda_estado = 'aclarar'
        if interpretacion.accion == 'consultar':
            propuesta.propuesta['_resultado_consulta'] = ejecutar_consulta(db, usuario, interpretacion.consulta)
        propuesta.propuesta['_anterior_id'] = datos.anterior_id
        propuesta.estado = agenda_estado or {'crear_tarea': 'pendiente', 'gestionar': 'pendiente', 'responder': 'respuesta',
                            'fuera_de_alcance': 'respuesta', 'consultar': 'respuesta'}.get(interpretacion.accion, 'aclarar')
    except HTTPException as error:
        # Aunque falte una referencia, el consumo de la consulta debe conservarse.
        propuesta.propuesta = {'accion': 'aclarar', 'aclaracion': str(error.detail), '_anterior_id': datos.anterior_id}
        propuesta.estado = 'aclarar'
    except (ValidationError, ValueError):
        propuesta.estado = 'error'
    db.add(propuesta)
    db.flush()
    if anterior and pendiente and propuesta.estado != 'error':
        anterior.estado = 'continuada'
    auditoria.registrar(db, usuario, auditoria.GENERAR, auditoria.PROPUESTA_TAREA, propuesta.id,
                       'Consultó a Mobilita', f'Estado: {propuesta.estado}; modelo: {propuesta.modelo}')
    db.commit()
    db.refresh(propuesta)
    if propuesta.estado == 'error':
        raise HTTPException(502, 'No pude preparar una propuesta válida. No se guardaron cambios. Conserva tu texto y prueba con una solicitud más breve o un cliente a la vez.')
    return respuesta(propuesta, db, usuario)


@router.post('/{propuesta_id}/confirmar', response_model=schemas.TareaRespuesta)
def confirmar(propuesta_id: int, datos: Confirmacion, db: Session = Depends(database.obtener_db),
              usuario: models.Usuario = Depends(seguridad.usuario_actual)):
    propuesta = obtener_propuesta(db, propuesta_id, usuario)
    if propuesta.estado == 'confirmada':
        tarea = db.query(models.Tarea).filter(models.Tarea.id == propuesta.tarea_id).first()
        if not tarea:
            raise HTTPException(409, 'La tarea confirmada ya no existe; no se volverá a crear.')
        obtener_tarea_permitida(db, tarea.id, usuario)
        return tarea
    if propuesta.estado != 'pendiente':
        raise HTTPException(409, 'Esta propuesta no puede confirmarse.')
    if propuesta.propuesta.get('accion') != 'crear_tarea':
        raise HTTPException(409, 'Confirma las acciones desde su resumen de cambios.')
    vigente(propuesta)
    clientes = clientes_coincidentes(db, propuesta.propuesta['cliente'], usuario)
    lead = next((c for c in clientes if c.id == datos.lead_id), None)
    if not lead or lead.estado == 'Cerrado':
        raise HTTPException(409, 'Selecciona un lead coincidente que no esté cerrado.')
    # Bloqueo del lead: dos propuestas simultáneas del mismo cliente se serializan
    # antes de comprobar duplicados en PostgreSQL.
    lead = validar_cliente_tarea(db, lead.id, usuario)
    if lead.estado == 'Cerrado':
        raise HTTPException(409, 'El lead está cerrado. Revisa su ficha antes de continuar.')
    pendientes = db.query(models.Tarea).filter(
        models.Tarea.lead_id == lead.id, models.Tarea.estado != 'Completada'
    ).all()
    duplicada = next((t for t in pendientes if normalizar(t.titulo) == normalizar(datos.titulo)), None)
    if duplicada:
        raise HTTPException(409, {'codigo': 'tarea_duplicada',
            'mensaje': 'Esta tarea ya existe para este lead. Revisa la tarea pendiente.',
            'tarea_id': duplicada.id, 'lead_id': lead.id})
    tarea = registrar_tarea(db, schemas.TareaCrear(**datos.model_dump(), estado='Pendiente'), usuario)
    propuesta.estado = 'confirmada'
    propuesta.tarea_id = tarea.id
    propuesta.confirmacion = datos.model_dump()
    auditoria.registrar(db, usuario, auditoria.ACTUALIZAR, auditoria.PROPUESTA_TAREA, propuesta.id,
                       f'Confirmó la tarea {tarea.titulo}', f'Tarea #{tarea.id}; lead #{lead.id}')
    db.commit()
    db.refresh(tarea)
    return tarea


@router.post('/{propuesta_id}/cancelar')
def cancelar(propuesta_id: int, db: Session = Depends(database.obtener_db),
             usuario: models.Usuario = Depends(seguridad.usuario_actual)):
    propuesta = obtener_propuesta(db, propuesta_id, usuario)
    if propuesta.estado == 'confirmada':
        raise HTTPException(409, 'La tarea ya está guardada. Cancelar no la elimina.')
    if propuesta.estado != 'cancelada':
        propuesta.estado = 'cancelada'
        auditoria.registrar(db, usuario, auditoria.ACTUALIZAR, auditoria.PROPUESTA_TAREA,
                           propuesta.id, 'Canceló la propuesta de tarea')
        db.commit()
    return {'estado': 'cancelada'}

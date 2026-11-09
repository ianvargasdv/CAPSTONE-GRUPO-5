"""Solicitudes por pasos, conservadas por el servidor y confirmadas una a una."""
from copy import deepcopy
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

import auditoria
import database
import models
import schemas
import seguridad
from acciones_mobilita import Operacion, validar_plan, resolver, ejecutar_plan, crear_ficha, ETIQUETAS, TIPOS
from tareas_servicio import normalizar, validar_cliente_tarea

router = APIRouter(prefix='/asistente/conversacion', tags=['Conversación de Mobilita'])


class Bloque(BaseModel):
    model_config = {'extra': 'forbid'}
    cliente: schemas.Nombre | None = None
    operaciones: list[Operacion] = Field(default_factory=list, max_length=5)
    pregunta: schemas.TextoLargo | None = None


def actual(contenido):
    return next((i for i, b in enumerate(contenido.get('_agenda', [])) if b['estado'] == 'pendiente'), None)


def crear_agenda(bloques, evidencia):
    if not 1 <= len(bloques) <= 5:
        raise ValueError('Divide la solicitud en un máximo de cinco bloques.')
    agenda = []
    for b in bloques:
        bloque = Bloque.model_validate(b)
        if bloque.cliente and normalizar(bloque.cliente) not in normalizar(evidencia):
            raise ValueError('El cliente no aparece en la solicitud.')
        validar_origen(bloque.operaciones, evidencia)
        agenda.append({**bloque.model_dump(mode='json'), 'estado': 'pendiente'})
    return {'accion': 'gestionar', '_agenda': agenda, '_recibos': {}}


def validar_origen(operaciones, evidencia):
    for op in operaciones:
        op = Operacion.model_validate(op)
        for campo in ('nombre', 'email'):
            if op.tipo in {'crear_lead', 'corregir_nombre'} and op.datos.get(campo) and normalizar(str(op.datos[campo])) not in normalizar(evidencia):
                raise ValueError('El nombre o correo propuesto no aparece en lo que indicaste.')


def activar(db, usuario, contenido):
    """Prepara el bloque actual sin escribir contactos, tareas ni fichas."""
    from tareas_chat import clientes_coincidentes
    c = deepcopy(contenido)
    for k in ('_operaciones', '_lead_id', '_cliente_nombre', '_opciones_cliente', '_nuevo_lead', '_resultado_consulta', '_errores_formato'):
        c.pop(k, None)
    i = actual(c)
    if i is None:
        c['aclaracion'] = 'Terminamos las solicitudes: puedes ver cuáles se guardaron y cuáles descartaste.'
        return c, 'confirmada'
    b = c['_agenda'][i]
    c['_paso'] = uuid4().hex
    c['cliente'] = b.get('cliente')
    c['aclaracion'] = b.get('pregunta') or f'¿Qué necesitas hacer con {b.get("cliente") or "este cliente"}? Indica el contacto, seguimiento o dato que quieres preparar.'
    if not b.get('cliente'):
        c['aclaracion'] = b.get('pregunta') or '¿A qué cliente corresponde esta solicitud? Indica su nombre.'
        return c, 'aclarar'
    if not b.get('operaciones'):
        return c, 'aclarar'
    for op in b['operaciones']:
        if op['tipo'] == 'crear_lead' and 'nombre' not in op['datos']:
            op['datos']['nombre'] = b['cliente']
    try:
        plan = validar_plan(b['operaciones'])
    except (ValidationError, ValueError) as error:
        if isinstance(error, ValidationError):
            errores = error.errors()
            campos = list(dict.fromkeys(str(e['loc'][-1]) for e in errores if e['type'] != 'extra_forbidden'))
            nombres = {'nombre': 'nombre', 'email': 'correo válido', 'fecha_hora': 'fecha y hora con zona horaria',
                       'titulo': 'título de la tarea', 'motivo': 'motivo de la solicitud',
                       'estado': 'estado del registro', 'prioridad': 'prioridad', 'telefono': 'teléfono válido',
                       'fecha_limite': 'fecha límite', 'tipo': 'tipo de contacto', 'tipo_operacion': 'compra o arriendo',
                       'duracion_minutos': 'duración de la visita', 'modalidad': 'modalidad de la visita'}
            nombres.update({'tipo_propiedad_buscada': 'tipo de propiedad', 'comunas_interes': 'comunas de interés',
                            'presupuesto_min': 'presupuesto mínimo', 'presupuesto_max': 'presupuesto máximo'})
            c['aclaracion'] = ('Para preparar esta solicitud, necesito revisar: ' + ', '.join(nombres.get(k, 'un dato del registro') for k in campos)
                              + '. Indícame esos datos; conservaré las demás solicitudes.') if campos else (
                'Tengo tu solicitud, pero necesito reorganizar los datos de la propuesta. Puedes pedirme que la revise; no se ha guardado nada.')
            c['_errores_formato'] = [{'campo': str(e['loc'][-1]), 'problema': e['type']} for e in errores]
        else:
            c['aclaracion'] = str(error)
        return c, 'aclarar'
    if plan.operaciones[0].tipo == 'crear_lead':
        c['_nuevo_lead'] = True
        c['_cliente_nombre'] = plan.operaciones[0].datos['nombre']
        c['_operaciones'] = [{**plan.operaciones[0].model_dump(mode='json'), 'etiqueta': ETIQUETAS['crear_lead']}]
        c['aclaracion'] = 'Revisa la ficha nueva. Se asignará a tu cuenta después de confirmar.'
        return c, 'pendiente'
    clientes = clientes_coincidentes(db, b['cliente'], usuario)
    if b.get('elegido_id') is not None:
        clientes = [l for l in clientes if l.id == b['elegido_id']]
    if len(clientes) > 1:
        c['_opciones_cliente'] = [{'id': l.id, 'nombre': l.nombre, 'estado': l.estado} for l in clientes[:10]]
        c['aclaracion'] = f'Hay varios clientes que coinciden con «{b["cliente"]}». Elige al correcto; conservaré lo que pediste.'
        if len(clientes) > 10:
            c['aclaracion'] += ' Se muestran diez coincidencias; también puedes indicar un nombre más completo.'
        return c, 'aclarar'
    if not clientes:
        c['aclaracion'] = 'No encontré una coincidencia disponible para tu cuenta. ¿Cuál es el nombre registrado del cliente?'
        return c, 'aclarar'
    lead = clientes[0]
    if lead.estado == 'Cerrado' and any(o.tipo != 'solicitar_archivo' for o in plan.operaciones):
        c['aclaracion'] = 'El lead está cerrado. Pide a administración revisar su ficha o descarta esta solicitud para continuar.'
        return c, 'aclarar'
    try:
        c['_operaciones'] = resolver(db, lead, plan)
    except HTTPException as error:
        c['aclaracion'] = str(error.detail) + ' Conservé las demás solicitudes.'
        return c, 'aclarar'
    c['_lead_id'], c['_cliente_nombre'] = lead.id, lead.nombre
    c['aclaracion'] = 'Revisa los cambios de este cliente y confirma para guardarlos.'
    return c, 'pendiente'


def resumen(contenido):
    return [{'numero': i + 1, 'cliente': b.get('cliente') or 'Cliente por indicar', 'estado': b['estado'],
             'acciones': [ETIQUETAS[o['tipo']] for o in b.get('operaciones', [])]}
            for i, b in enumerate(contenido.get('_agenda', []))]


def contexto_pendiente(contenido):
    i = actual(contenido)
    if i is None:
        return None
    b = contenido['_agenda'][i]
    return {'solicitud_actual': {k: v for k, v in b.items() if k not in {'elegido_id', 'estado'}},
            'cliente_elegido': contenido.get('_cliente_nombre'), 'avance': resumen(contenido),
            'correcciones_de_formato': contenido.get('_errores_formato', []),
            'instruccion': 'Completa sólo este bloque con la aclaración. El servidor conserva los demás. No repitas lo guardado.'}


def sustituir_actual(contenido, bloque):
    c = deepcopy(contenido)
    i = actual(c)
    if i is None:
        raise ValueError('No hay una solicitud pendiente.')
    anterior = c['_agenda'][i]
    nuevo = Bloque.model_validate(bloque).model_dump(mode='json')
    for op in nuevo['operaciones']:
        coincidentes = [o for o in anterior.get('operaciones', []) if o['tipo'] == op['tipo'] and o.get('referencia') == op.get('referencia')]
        if len(coincidentes) == 1:
            anteriores_validos = {k: v for k, v in coincidentes[0]['datos'].items() if k in TIPOS[op['tipo']].model_fields}
            op['datos'] = {**anteriores_validos, **op['datos']}
    c['_agenda'][i] = {**nuevo, 'estado': 'pendiente'}
    if anterior.get('elegido_id') and normalizar(anterior.get('cliente')) == normalizar(bloque.get('cliente')):
        c['_agenda'][i]['elegido_id'] = anterior['elegido_id']
    return c


def confirmar_paso(db, usuario, propuesta, paso):
    from tareas_chat import vigente, respuesta
    vigente(propuesta)
    c = deepcopy(propuesta.propuesta)
    if propuesta.estado == 'continuada':
        raise HTTPException(409, 'Continúa desde el último mensaje de la conversación.')
    if paso and paso in c.get('_recibos', {}):
        return {'mensaje': 'Este paso ya estaba guardado; no se repitió.', 'siguiente': respuesta(propuesta, db, usuario)}
    if not paso or paso != c.get('_paso') or propuesta.estado != 'pendiente':
        raise HTTPException(409, 'La propuesta cambió. Revisa el paso actual antes de confirmar.')
    i = actual(c)
    if i is None:
        raise HTTPException(409, 'No hay acciones pendientes.')
    try:
        if c.get('_nuevo_lead'):
            lead = crear_ficha(db, usuario, c['_operaciones'][0]['datos'])
        else:
            lead = validar_cliente_tarea(db, c['_lead_id'], usuario)
            solo_archivo = all(o['tipo'] == 'solicitar_archivo' for o in c['_operaciones'])
            if lead.archivado or (lead.estado == 'Cerrado' and not solo_archivo):
                raise HTTPException(409, 'El cliente ya no permite esta acción. Revisa su ficha.')
            ejecutar_plan(db, usuario, lead, c['_operaciones'])
        c['_agenda'][i]['estado'] = 'guardado'
        c['_recibos'][paso] = {'lead_id': lead.id, 'bloque': i}
        mensaje = ('Solicitud enviada a administración; el lead sigue intacto.'
                   if c['_agenda'][i]['operaciones'][0]['tipo'] == 'solicitar_archivo'
                   else f'Guardé la solicitud de {lead.nombre}.')
        contenido, estado = activar(db, usuario, c)
        propuesta.propuesta, propuesta.estado = contenido, estado
        propuesta.confirmacion = {'ultimo_paso': paso, 'lead_id': lead.id}
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {'mensaje': mensaje, 'siguiente': respuesta(propuesta, db, usuario)}


class Elegir(BaseModel):
    model_config = {'extra': 'forbid'}
    lead_id: int = Field(gt=0, strict=True)
    paso: str = Field(min_length=1, max_length=40)


@router.post('/{propuesta_id}/elegir')
def elegir_cliente(propuesta_id: int, datos: Elegir, db: Session = Depends(database.obtener_db),
                   usuario=Depends(seguridad.usuario_actual)):
    from tareas_chat import obtener_propuesta, vigente, respuesta, clientes_coincidentes
    p = obtener_propuesta(db, propuesta_id, usuario)
    vigente(p)
    c = deepcopy(p.propuesta or {})
    if p.estado != 'aclarar' or datos.paso != c.get('_paso') or not c.get('_opciones_cliente'):
        raise HTTPException(409, 'La selección ya no está disponible. Continúa desde el último mensaje.')
    permitidos = {l.id for l in clientes_coincidentes(db, c['cliente'], usuario)}
    if datos.lead_id not in permitidos or datos.lead_id not in {l['id'] for l in c['_opciones_cliente']}:
        raise HTTPException(404, 'Cliente no disponible para esta selección.')
    c['_agenda'][actual(c)]['elegido_id'] = datos.lead_id
    p.propuesta, p.estado = activar(db, usuario, c)
    db.commit()
    return respuesta(p, db, usuario)


class Descartar(BaseModel):
    model_config = {'extra': 'forbid'}
    paso: str = Field(min_length=1, max_length=40)
    todos: bool = False


class Ajustar(BaseModel):
    model_config = {'extra': 'forbid'}
    paso: str | None = Field(default=None, min_length=1, max_length=40)


@router.post('/{propuesta_id}/ajustar')
def ajustar_paso(propuesta_id: int, datos: Ajustar, db: Session = Depends(database.obtener_db),
                 usuario=Depends(seguridad.usuario_actual)):
    from tareas_chat import obtener_propuesta, vigente, respuesta
    p = obtener_propuesta(db, propuesta_id, usuario)
    vigente(p)
    c = deepcopy(p.propuesta or {})
    if p.estado != 'pendiente' or c.get('accion') != 'gestionar':
        raise HTTPException(409, 'Sólo puedes ajustar el paso pendiente actual.')
    if not c.get('_agenda'):
        c.update(crear_agenda([{'cliente': c.get('cliente'), 'operaciones': c.get('operaciones', [])}], p.solicitud + ' ' + str(c)))
    elif datos.paso != c.get('_paso') or actual(c) is None:
        raise HTTPException(409, 'Sólo puedes ajustar el paso pendiente actual.')
    c.pop('_operaciones', None)
    c['_paso'] = uuid4().hex
    c['aclaracion'] = '¿Qué quieres corregir de esta solicitud? Conservo los datos y los demás pasos; todavía no guardaré nada.'
    p.propuesta, p.estado = c, 'aclarar'
    db.commit()
    return respuesta(p, db, usuario)


@router.post('/{propuesta_id}/descartar')
def descartar_paso(propuesta_id: int, datos: Descartar, db: Session = Depends(database.obtener_db),
                   usuario=Depends(seguridad.usuario_actual)):
    from tareas_chat import obtener_propuesta, vigente, respuesta
    p = obtener_propuesta(db, propuesta_id, usuario)
    vigente(p)
    c = deepcopy(p.propuesta or {})
    if p.estado not in {'pendiente', 'aclarar', 'respuesta'} or datos.paso != c.get('_paso') or actual(c) is None:
        raise HTTPException(409, 'No hay un paso vigente para descartar.')
    i = actual(c)
    for n, b in enumerate(c['_agenda']):
        if b['estado'] == 'pendiente' and (datos.todos or n == i):
            b['estado'] = 'descartado'
    p.propuesta, p.estado = activar(db, usuario, c)
    auditoria.registrar(db, usuario, auditoria.ACTUALIZAR, auditoria.PROPUESTA_TAREA, p.id,
                       'Descartó solicitudes pendientes de Mobilita')
    db.commit()
    return respuesta(p, db, usuario)

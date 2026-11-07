"""Validaciones y registro común de tareas manuales y confirmadas desde el chat."""
import unicodedata
from datetime import date

from fastapi import HTTPException
import auditoria
import models


def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto or '').lower()
    return ' '.join(''.join(c for c in texto if not unicodedata.combining(c)).split())


def tareas_permitidas(db, usuario):
    consulta = db.query(models.Tarea)
    if usuario.rol != 'admin':
        consulta = consulta.join(models.Lead, models.Tarea.lead_id == models.Lead.id).filter(
            models.Lead.ejecutivo_id == usuario.id)
    return consulta


def validar_cliente_tarea(db, lead_id, usuario):
    """Bloquea el lead para que no cambie de responsable durante una escritura."""
    if lead_id is None:
        if usuario.rol != 'admin':
            raise HTTPException(403, 'Selecciona un lead de tu cartera para esta tarea.')
        return None
    consulta = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if usuario.rol != 'admin':
        consulta = consulta.filter(models.Lead.ejecutivo_id == usuario.id)
    lead = consulta.with_for_update().populate_existing().first()
    if not lead:
        raise HTTPException(404, 'Lead no encontrado o no disponible para tu cuenta')
    return lead


def obtener_tarea_permitida(db, tarea_id, usuario):
    tarea = tareas_permitidas(db, usuario).filter(models.Tarea.id == tarea_id).with_for_update(
        of=models.Tarea).populate_existing().first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    validar_cliente_tarea(db, tarea.lead_id, usuario)
    return tarea


def verificar_tarea_no_repetida(db, lead_id, titulo, descripcion, estado, excluir_id=None):
    if not lead_id or estado == 'Completada':
        return
    pendientes = db.query(models.Tarea).filter(
        models.Tarea.lead_id == lead_id, models.Tarea.estado != 'Completada'
    ).all()
    for pendiente in pendientes:
        if pendiente.id != excluir_id and normalizar(pendiente.titulo) == normalizar(titulo) and normalizar(pendiente.descripcion) == normalizar(descripcion):
            raise HTTPException(409, 'Ya existe una tarea pendiente igual para este cliente. Abre la existente en Tareas.')


def registrar_tarea(db, datos, usuario):
    """No confirma la transacción: el llamador guarda tarea y origen juntos."""
    validar_cliente_tarea(db, datos.lead_id, usuario)
    verificar_tarea_no_repetida(db, datos.lead_id, datos.titulo, datos.descripcion, datos.estado)
    tarea = models.Tarea(
        titulo=datos.titulo, descripcion=datos.descripcion, estado=datos.estado,
        prioridad=datos.prioridad, lead_id=datos.lead_id,
        fecha_limite=date.fromisoformat(datos.fecha_limite) if datos.fecha_limite else None,
    )
    db.add(tarea)
    db.flush()
    auditoria.registrar(db, usuario, auditoria.CREAR, auditoria.TAREA, tarea.id, f'Creó la tarea {tarea.titulo}')
    return tarea

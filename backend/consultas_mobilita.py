"""Consultas cerradas: permisos por sesión, resultados acotados y ninguna escritura."""
from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from sqlalchemy import func

import models


class Consulta(BaseModel):
    model_config = {'extra': 'forbid', 'strict': True}
    herramienta: Literal['cartera_resumen', 'tareas_pendientes', 'tareas_vencidas', 'propiedades_disponibles', 'ejecutivos_disponibles']
    alcance: Literal['mia', 'general'] = 'mia'


def ejecutar_consulta(db, usuario, consulta: Consulta):
    """La identidad viene de la sesión, nunca de parámetros propuestos por el LLM."""
    fecha = datetime.now(ZoneInfo('America/Santiago'))
    base = {'herramienta': consulta.herramienta, 'alcance': consulta.alcance,
            'fecha_consulta': fecha.isoformat(), 'limite': 10}
    if consulta.herramienta == 'ejecutivos_disponibles':
        # Es un directorio administrativo incluso si el modelo solicita alcance mia.
        base['alcance'] = 'general'
        if usuario.rol != 'admin':
            return {**base, 'permitida': False,
                    'mensaje': 'El listado de ejecutivos requiere una cuenta de administrador.'}
        # Outer join conserva los ejecutivos sin cartera; no contar filas con count(*).
        q = db.query(models.Usuario.id, models.Usuario.nombre, func.count(models.Lead.id)).outerjoin(
            models.Lead, models.Lead.ejecutivo_id == models.Usuario.id).filter(
            models.Usuario.rol == 'ejecutivo', models.Usuario.activo.is_(True)).group_by(
            models.Usuario.id, models.Usuario.nombre)
        total = q.count()
        filas = q.order_by(models.Usuario.nombre, models.Usuario.id).limit(10).all()
        mensaje = f'Ejecutivos activos: {total}.' if total else 'No hay ejecutivos activos registrados.'
        if filas:
            mensaje += '\n' + '\n'.join(
                f'• {nombre} · {cantidad} {"lead asignado" if cantidad == 1 else "leads asignados"}'
                for _, nombre, cantidad in filas)
        if total > 10:
            mensaje += '\nSe muestran los primeros 10 por nombre.'
        return {**base, 'permitida': True, 'total': total, 'mensaje': mensaje,
                'ejecutivos': [{'id': i, 'nombre': nombre, 'leads_asignados': cantidad}
                               for i, nombre, cantidad in filas]}
    if consulta.alcance == 'general' and usuario.rol != 'admin':
        return {**base, 'permitida': False,
                'mensaje': 'El resumen general requiere una cuenta de administrador. Puedes consultar tu cartera y sus tareas.'}
    propia = consulta.alcance == 'mia'
    datos_consulta = {}
    etiqueta = 'de tu cartera asignada' if propia else 'del CRM'
    if consulta.herramienta == 'cartera_resumen':
        q = db.query(models.Lead.estado, func.count(models.Lead.id))
        if propia:
            q = q.filter(models.Lead.ejecutivo_id == usuario.id)
        estados = q.group_by(models.Lead.estado).order_by(models.Lead.estado).all()
        total = sum(cantidad for _, cantidad in estados)
        detalle = '; '.join(f'{estado or "Sin estado"}: {cantidad}' for estado, cantidad in estados)
        mensaje = f'Leads {etiqueta}: {total}.' + (f' {detalle}.' if detalle else '')
    elif consulta.herramienta in {'tareas_pendientes', 'tareas_vencidas'}:
        # Las tareas actuales no tienen autor responsable: su alcance deriva del lead.
        q = db.query(models.Tarea.id, models.Tarea.titulo, models.Tarea.fecha_limite,
                     models.Tarea.estado, models.Lead.nombre).outerjoin(
                         models.Lead, models.Tarea.lead_id == models.Lead.id).filter(
                             models.Tarea.estado != 'Completada')
        if propia:
            q = q.filter(models.Lead.ejecutivo_id == usuario.id)
        vencidas = consulta.herramienta == 'tareas_vencidas'
        if vencidas:
            q = q.filter(models.Tarea.fecha_limite < fecha.date())
        total = q.count()
        filas = q.order_by(models.Tarea.fecha_limite.is_(None), models.Tarea.fecha_limite, models.Tarea.id).limit(10).all()
        lineas = [f'• #{i} · {nombre or "Sin lead"}: {titulo} · {estado} · '
                  f'{limite.isoformat() if limite else "Sin fecha"}' for i, titulo, limite, estado, nombre in filas]
        mensaje = f'Tareas {"vencidas" if vencidas else "sin completar"} {etiqueta}: {total}.'
        if lineas:
            mensaje += '\n' + '\n'.join(lineas)
    else:
        # Sólo columnas comerciales; propietario, captador y contactos nunca se seleccionan.
        q = db.query(models.Propiedad.id, models.Propiedad.titulo, models.Propiedad.comuna,
                     models.Propiedad.precio, models.Propiedad.moneda, models.Propiedad.tipo_operacion).filter(models.Propiedad.estado == 'Disponible')
        total = q.count()
        filas = q.order_by(models.Propiedad.id).limit(10).all()
        mensaje = f'{total} propiedades disponibles.' if total else 'No hay propiedades disponibles en el catálogo.'
        datos_consulta = {'propiedades': [{'id': i, 'titulo': titulo, 'comuna': comuna,
                                   'precio': precio, 'moneda': moneda, 'operacion': operacion}
                                  for i, titulo, comuna, precio, moneda, operacion in filas]}
    if total > 10 and consulta.herramienta in {'tareas_pendientes', 'tareas_vencidas'}:
        mensaje += '\nSe muestran las primeras 10. Consulta el listado del CRM para ver el resto.'
    return {**base, **datos_consulta, 'permitida': True, 'total': total, 'mensaje': mensaje}

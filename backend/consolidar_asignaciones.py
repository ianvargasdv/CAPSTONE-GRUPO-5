"""Copia el historial anterior sin borrarlo ni cambiar responsables actuales."""

from sqlalchemy import MetaData, Table, inspect, select


def consolidar_historial(conexion):
    """Debe ejecutarse dentro de una transacción, después de crear las columnas.

    El identificador de origen evita repetir importaciones. No se reconstruyen
    movimientos sin fecha: ante datos inválidos, la transacción debe revertirse.
    """
    if not inspect(conexion).has_table('historial_asignaciones'):
        return 0
    metadata = MetaData()
    origen = Table('historial_asignaciones', metadata, autoload_with=conexion)
    destino = Table('asignaciones_lead', metadata, autoload_with=conexion)
    requeridas = {
        'id', 'lead_id', 'ejecutivo_anterior_id', 'ejecutivo_anterior_nombre',
        'ejecutivo_nuevo_id', 'ejecutivo_nuevo_nombre', 'realizado_por_id',
        'realizado_por_email', 'fecha_creacion',
    }
    if not requeridas.issubset(origen.c.keys()):
        raise ValueError('El historial anterior no tiene la estructura esperada')
    usuarios = Table('usuarios', metadata, autoload_with=conexion)
    leads = Table('leads', metadata, autoload_with=conexion)
    nombres_usuario = {fila.id: fila.nombre for fila in conexion.execute(select(usuarios.c.id, usuarios.c.nombre))}
    nombres_lead = {fila.id: fila.nombre for fila in conexion.execute(select(leads.c.id, leads.c.nombre))}
    importados = set(conexion.execute(select(destino.c.historial_origen_id)).scalars())
    pendientes = []
    for fila in conexion.execute(select(origen).order_by(origen.c.id)).mappings():
        if fila['id'] in importados:
            continue
        if fila['fecha_creacion'] is None:
            raise ValueError('Hay movimientos sin fecha; no se importará una fecha inventada')
        datos = {
            'historial_origen_id': fila['id'],
            'lead_id': fila['lead_id'] if fila['lead_id'] in nombres_lead else None,
            'lead_nombre': nombres_lead.get(fila['lead_id'], 'Lead eliminado'),
            'anterior_id': fila['ejecutivo_anterior_id'] if fila['ejecutivo_anterior_id'] in nombres_usuario else None,
            'anterior_nombre': fila['ejecutivo_anterior_nombre'],
            'nuevo_id': fila['ejecutivo_nuevo_id'] if fila['ejecutivo_nuevo_id'] in nombres_usuario else None,
            'nuevo_nombre': fila['ejecutivo_nuevo_nombre'] or 'Nombre no registrado',
            # La tabla anterior guardaba el correo, no el nombre del autor.
            # Conservamos ese correo por separado; el nombre se resuelve hoy.
            'autor_id': fila['realizado_por_id'] if fila['realizado_por_id'] in nombres_usuario else None,
            'autor_nombre': nombres_usuario.get(fila['realizado_por_id'], 'Autor no registrado'),
            'autor_email': fila['realizado_por_email'],
            'fecha_creacion': fila['fecha_creacion'],
        }
        for campo in ['lead_nombre', 'anterior_nombre', 'nuevo_nombre', 'autor_nombre', 'autor_email']:
            limite = destino.c[campo].type.length
            if datos[campo] is not None and len(datos[campo]) > limite:
                raise ValueError('Un dato del historial excede la longitud permitida; no se truncará')
        pendientes.append(datos)
    if pendientes:
        conexion.execute(destino.insert(), pendientes)
    return len(pendientes)

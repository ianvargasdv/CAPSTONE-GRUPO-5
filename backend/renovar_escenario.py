"""Renueva exclusivamente datos ficticios. Sin --aplicar no guarda cambios."""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ACCIONES = [
 ('Confirmar presupuesto disponible', 'Precisar el rango de presupuesto y su moneda antes de proponer alternativas.'),
 ('Revisar condiciones de arriendo', 'Consultar requisitos del contrato, garantía y plazo mínimo.'),
 ('Comparar alternativas de vivienda', 'Preparar una comparación de precio, comuna y distribución de las propiedades de interés.'),
 ('Consultar gastos comunes', 'Solicitar el monto vigente y qué servicios incluye.'),
 ('Coordinar horario de visita', 'Proponer dos horarios y confirmar disponibilidad del cliente antes de agendar.'),
 ('Solicitar plano del inmueble', 'Revisar la distribución y confirmar que corresponda a la propiedad seleccionada.'),
 ('Revisar financiamiento', 'Consultar el estado del financiamiento sin asumir una aprobación bancaria.'),
 ('Confirmar estacionamiento', 'Verificar cantidad, disponibilidad y si está incluido en el precio.'),
 ('Consultar disponibilidad de bodega', 'Confirmar si existe bodega y las condiciones para utilizarla.'),
 ('Preparar ficha para el cliente', 'Reunir precio, superficie y características verificadas del inmueble.'),
 ('Confirmar fecha de mudanza', 'Precisar desde cuándo necesita disponer de la vivienda.'),
 ('Revisar documentación comercial', 'Identificar los antecedentes pendientes sin pedir documentos sensibles por el chat.'),
 ('Consultar orientación y luz natural', 'Confirmar orientación y condiciones de iluminación de la vivienda.'),
 ('Confirmar requisitos de mascotas', 'Consultar las condiciones del inmueble y del edificio para mascotas.'),
 ('Revisar conectividad del sector', 'Consultar qué servicios y transporte son prioritarios para el cliente.'),
 ('Preparar propuesta comercial', 'Revisar precio y condiciones antes de presentar una propuesta al cliente.'),
 ('Consultar condiciones de reserva', 'Confirmar requisitos, plazos y condiciones con el responsable del inmueble.'),
 ('Revisar observaciones de visita', 'Consultar dudas pendientes antes de avanzar en la negociación.'),
 ('Confirmar superficie requerida', 'Precisar superficie mínima y espacios que el cliente considera indispensables.'),
 ('Revisar dormitorios necesarios', 'Confirmar cantidad de dormitorios y uso esperado de los espacios.'),
 ('Consultar accesibilidad del edificio', 'Verificar ascensor, accesos y necesidades específicas del cliente.'),
 ('Confirmar interés en la propiedad', 'Preguntar si desea continuar con esta alternativa o ajustar su búsqueda.'),
 ('Revisar condiciones de entrega', 'Consultar disponibilidad, equipamiento incluido y estado de entrega.'),
 ('Preparar alternativas de comuna', 'Revisar si acepta sectores adicionales dentro de su presupuesto.'),
 ('Consultar terraza y espacios exteriores', 'Precisar las preferencias del cliente y verificar los datos del catálogo.'),
 ('Revisar próximos pasos del negocio', 'Definir con el cliente la siguiente gestión y una fecha de seguimiento.'),
]


def renovar(db, ahora, aplicar=False, carpeta_respaldo=None):
    import models
    import auditoria
    from sqlalchemy import func
    ahora = ahora.astimezone(ZoneInfo('America/Santiago'))
    hoy = ahora.date()
    marca = f'Renovación del escenario de demostración · {hoy.isoformat()}'
    if db.query(models.Auditoria.id).filter_by(descripcion=marca).first():
        return {'ya_aplicado': True}
    # Se exigen las dos marcas: flag de prueba y dominio reservado, nunca un nombre.
    leads = db.query(models.Lead).filter(models.Lead.es_demo.is_(True),
        models.Lead.email.like('%@example.test')).order_by(models.Lead.id).all()
    ids = [l.id for l in leads]
    tareas = db.query(models.Tarea).filter(models.Tarea.lead_id.in_(ids)).order_by(models.Tarea.id).all()
    visitas = db.query(models.Visita).filter(models.Visita.lead_id.in_(ids)).order_by(models.Visita.id).all()
    negocios = db.query(models.Oportunidad).filter(models.Oportunidad.lead_id.in_(ids)).order_by(models.Oportunidad.id).all()
    notas_semilla = [
        'Confirmó la comuna; queda pendiente precisar estacionamientos y superficie.',
        'Solicitó pausar el contacto; no desea nuevos mensajes.',
        'Confirmó crédito preaprobado y disponibilidad para visitar el sábado.',
        'Se enviaron fichas de Ñuñoa y Macul. Prefiere orientación norte.',
        'Busca arriendo inmediato y acepta coordinar en horario vespertino.',
        'Envió antecedentes iniciales para evaluación.',
        'Pausó la búsqueda hasta terminar su evaluación bancaria.',
    ]
    interacciones=db.query(models.Interaccion).filter(models.Interaccion.lead_id.in_(ids),
        models.Interaccion.notas.in_(notas_semilla)).order_by(models.Interaccion.id).all()
    propiedades = db.query(models.Propiedad).filter(models.Propiedad.codigo_interno.like('PRUEBA-CRM-%')).all()
    resumen = {'leads':len(leads), 'tareas':len(tareas), 'visitas':len(visitas),
               'negocios':len(negocios), 'propiedades':len(propiedades),
               'interacciones_simuladas':len(interacciones), 'fecha_base':str(hoy)}
    if not aplicar:
        return resumen
    if not carpeta_respaldo:
        raise ValueError('Se requiere una carpeta de respaldo antes de modificar datos.')
    campos = {
        'leads':(leads,['id','fecha_creacion','proxima_accion','fecha_proxima_accion']),
        'tareas':(tareas,['id','titulo','descripcion','estado','prioridad','fecha_limite']),
        'visitas':(visitas,['id','fecha_hora']),
        'oportunidades':(negocios,['id','fecha_cierre_estimada','fecha_cierre']),
        'propiedades':(propiedades,['id','fecha_disponibilidad']),
        'interacciones':(interacciones,['id','fecha_creacion']),
    }
    respaldo = {tabla:[{c:getattr(fila,c) for c in columnas} for fila in filas]
                for tabla,(filas,columnas) in campos.items()}
    carpeta = Path(carpeta_respaldo); carpeta.mkdir(parents=True,exist_ok=True)
    ruta = carpeta / f'escenario_antes_{ahora.strftime("%Y%m%d_%H%M%S_%f")}.json'
    with ruta.open('x',encoding='utf-8') as archivo:
        json.dump(respaldo,archivo,ensure_ascii=False,default=str,indent=2)
    pendientes = {}
    for i,t in enumerate(tareas):
        titulo,descripcion=ACCIONES[i % len(ACCIONES)]
        t.titulo=titulo; t.descripcion=descripcion
        t.estado='Completada' if i%6==5 else 'En Progreso' if i%3==0 else 'Pendiente'
        t.prioridad=['Alta','Media','Media','Baja'][i%4]
        t.fecha_limite=hoy+timedelta(days=i%10) if t.estado!='Completada' else hoy-timedelta(days=1)
        if t.estado!='Completada': pendientes.setdefault(t.lead_id,t)
    for i,l in enumerate(leads):
        # Conservar el ingreso: hay auditoría y análisis anteriores asociados al lead.
        tarea=pendientes.get(l.id)
        l.proxima_accion=tarea.titulo if tarea else None
        l.fecha_proxima_accion=tarea.fecha_limite if tarea else None
    for i,interaccion in enumerate(interacciones):
        interaccion.fecha_creacion=(ahora-timedelta(days=1+i%2)).replace(hour=11,minute=0,second=0,microsecond=0)
    primer_dia=1 if ahora.hour>=10 else 0
    for i,v in enumerate(visitas):
        dia=hoy+timedelta(days=primer_dia+i%7) if v.estado in ('Programada','Confirmada') else hoy-timedelta(days=2+i%3)
        v.fecha_hora=datetime(dia.year,dia.month,dia.day,10+2*(i//7),0,tzinfo=ZoneInfo('America/Santiago'))
    for i,o in enumerate(negocios):
        cerrada=o.etapa in ('Ganada','Perdida')
        o.fecha_cierre_estimada=hoy+timedelta(days=7+i%21) if not cerrada else hoy-timedelta(days=2)
        o.fecha_cierre=hoy-timedelta(days=2) if cerrada else None
    for i,p in enumerate(propiedades):
        if p.estado=='Disponible': p.fecha_disponibilidad=hoy+timedelta(days=i%5)
    auditoria.registrar(db,None,auditoria.ACTUALIZAR,'escenario',None,marca,
        'Renovación solicitada del escenario ficticio. Fechas y tareas simuladas; no representa gestiones reales. '+json.dumps(resumen))
    db.flush()
    vencidas=db.query(func.count(models.Tarea.id)).filter(models.Tarea.lead_id.in_(ids),
        models.Tarea.estado!='Completada',models.Tarea.fecha_limite<hoy).scalar()
    if vencidas: raise ValueError('El escenario conserva tareas pendientes vencidas.')
    return {**resumen,'vencidas':vencidas,'respaldo':str(ruta)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar',action='store_true')
    args=parser.parse_args()
    import database
    with database.SessionLocal() as db:
        try:
            resultado=renovar(db,datetime.now(ZoneInfo('America/Santiago')),args.aplicar,
                Path(__file__).parent.parent/'.codex-temp'/'respaldos')
            if args.aplicar: db.commit()
            print(json.dumps(resultado,ensure_ascii=True))
        except Exception:
            db.rollback(); raise


if __name__=='__main__': main()

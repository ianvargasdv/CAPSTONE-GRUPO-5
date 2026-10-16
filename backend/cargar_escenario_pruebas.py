"""Escenario ficticio con nombres naturales. No borra ni actualiza registros.

Uso: python cargar_escenario_pruebas.py --aplicar
Sin --aplicar sólo muestra el tamaño del escenario, sin conectarse a la base.
Las claves estables impiden duplicar la carga secuencial. No ejecutar en paralelo.
"""
import argparse
from datetime import datetime, timedelta, timezone

NOMBRES = [
    'Javiera Contreras', 'Nicolás Araya', 'Daniela Sepúlveda', 'Felipe Muñoz',
    'Antonia Carrasco', 'Sebastián Navarro', 'Catalina Espinoza', 'Tomás Salinas',
    'Francisca Paredes', 'Benjamín Soto', 'Josefina Valdés', 'Vicente Cárdenas',
    'Constanza Aguilera', 'Ignacio Sandoval', 'Trinidad Figueroa', 'Gabriel Cortés',
    'Paula Henríquez', 'Cristóbal Riquelme', 'Renata Saavedra', 'Alonso Vera',
    'María José Tapia', 'Joaquín Leiva', 'Florencia Bustos', 'Diego Alvarado',
]
SECTORES = [('Ñuñoa', 'Plaza Ñuñoa'), ('Macul', 'Los Plátanos'),
    ('La Reina', 'Príncipe de Gales'), ('Providencia', 'Manuel Montt'),
    ('San Miguel', 'El Llano'), ('Peñalolén', 'Los Presidentes')]
MARCA = 'Escenario ficticio de pruebas CRM v1.'


def catalogo():
    propiedades = []
    for i in range(18):
        comuna, sector = SECTORES[i % len(SECTORES)]
        tipo = 'Casa' if i % 3 == 2 else 'Departamento'
        operacion = 'Arriendo' if i % 4 == 0 else 'Compra'
        moneda = 'UF' if operacion == 'Compra' and i % 2 else 'CLP'
        precio = (650000 + i * 15000) if operacion == 'Arriendo' else (
            3800 + i * 180 if moneda == 'UF' else 125000000 + i * 6500000)
        util = 52 + i * 3
        propiedades.append(dict(codigo_interno=f'PRUEBA-CRM-{i+1:03d}',
            titulo=f'{tipo} en {sector}, sector {i//6+1}', tipo=tipo,
            tipo_operacion=operacion, precio=precio, moneda=moneda,
            direccion=f'Sector {sector}, {comuna} (ubicación referencial ficticia)',
            comuna=comuna, dormitorios=3 if tipo == 'Casa' else 2, banos=2,
            estado=(
                'Reservada' if i == 13 else 'Vendida' if i == 14 else
                'Arrendada' if i == 16 else 'Retirada' if i == 17 else 'Disponible'),
            superficie_util=util, superficie_total=util+85 if tipo=='Casa' else util+8,
            estacionamientos=1+(i%2), bodega=i%2==0, gastos_comunes=75000+i*2500,
            descripcion=f'{MARCA} Inmueble inventado para revisar ficha, búsqueda y seguimiento; no es una oferta real.',
            caracteristicas='Orientación norte, cocina equipada y terraza.' if tipo=='Departamento' else 'Patio y espacio de estacionamiento.',
            fotografias=[], propietario_nombre=f'Propietario ficticio {i+1}',
            propietario_email=f'propietario.{i+1:03d}@example.test',
            propietario_telefono=None, captador='Equipo de pruebas'))
    return propiedades


def cargar():
    import database
    import models
    ahora = datetime.now(timezone.utc)
    hoy = ahora.date()
    cuentas = {k:0 for k in ['leads','propiedades','intereses','interacciones','tareas','oportunidades','visitas']}
    with database.SessionLocal() as db:
        def agregar(objeto, entidad, grupo, etiqueta):
            db.add(objeto); db.flush()
            db.add(models.Auditoria(accion='crear', entidad=entidad, entidad_id=objeto.id,
                descripcion=f'Carga ficticia de pruebas: {etiqueta}'[:250],
                detalle=MARCA+' Carga automatizada; no representa un contacto o visita real.'))
            cuentas[grupo] += 1
            return objeto

        try:
            responsables = db.query(models.Usuario).filter(models.Usuario.activo.is_(True)).order_by(models.Usuario.id).all()
            propiedades = []
            for datos in catalogo():
                encontrados = db.query(models.Propiedad).filter_by(codigo_interno=datos['codigo_interno']).all()
                if len(encontrados)>1 or (encontrados and not (encontrados[0].descripcion or '').startswith(MARCA)):
                    raise ValueError('Un código de prueba ya está ocupado por otro registro; no se modificó la base.')
                propiedad = encontrados[0] if encontrados else agregar(models.Propiedad(**datos),'propiedad','propiedades',datos['titulo'])
                propiedades.append(propiedad)

            for i, nombre in enumerate(NOMBRES):
                correo = f'cliente.escenario.{i+1:03d}@example.test'
                lead = db.query(models.Lead).filter_by(email=correo).first()
                if lead and not lead.es_demo:
                    raise ValueError('Un correo reservado del escenario está ocupado; no se modificó la base.')
                # No se reponen relaciones de un registro que el usuario pudo haber editado.
                if lead:
                    continue
                propiedad = propiedades[i % len(propiedades)]
                estado = ['Nuevo','Contactado','Calificado','Contactado'][i%4]
                cerrado = i in (14,17)
                if cerrado: estado='Cerrado'
                responsable = responsables[i%len(responsables)] if responsables else None
                incompleto = i in (0,6,12,18)
                lead = agregar(models.Lead(nombre=nombre,email=correo,telefono=None,
                    es_demo=True,estado=estado,prioridad=['Alta','Media','Baja'][i%3],
                    ejecutivo_id=responsable.id if responsable else None,
                    tipo_operacion=propiedad.tipo_operacion,tipo_propiedad_buscada=propiedad.tipo,
                    comunas_interes=propiedad.comuna,
                    presupuesto_min=None if incompleto else int(propiedad.precio*.85),
                    presupuesto_max=None if incompleto else int(propiedad.precio*1.1),
                    moneda=propiedad.moneda,dormitorios_min=propiedad.dormitorios,banos_min=2,
                    plazo_decision='0-3 meses',financiamiento='En evaluación',origen='Demo capstone',
                    proxima_accion=None if cerrado else 'Confirmar requisitos de estacionamiento y superficie de terreno',
                    fecha_proxima_accion=None if cerrado else hoy+timedelta(days=(i%7)-2),
                    fecha_creacion=ahora-timedelta(days=(i%12)+1)), 'lead','leads',nombre)
                agregar(models.Interes(lead_id=lead.id,propiedad_id=propiedad.id,nivel_interes=['Alto','Medio','Bajo'][i%3],
                    notas='Le interesa la distribución; falta confirmar estacionamientos.'),'interes','intereses',nombre)
                if estado != 'Nuevo':
                    agregar(models.Interaccion(lead_id=lead.id,tipo=['Llamada','Email','WhatsApp'][i%3],
                        notas='Solicitó pausar el contacto; no desea nuevos mensajes.' if cerrado else
                            'Confirmó la comuna; queda pendiente precisar estacionamientos y superficie.',
                        fecha_creacion=ahora-timedelta(days=(i%6)+1)), 'interaccion','interacciones',nombre)
                if not cerrado:
                    agregar(models.Tarea(lead_id=lead.id,titulo='Completar requisitos de búsqueda',
                        descripcion='Confirmar cantidad de estacionamientos y, si busca casa, superficie de terreno.',
                        estado='En Progreso' if i%3==0 else 'Pendiente',prioridad='Media',
                        fecha_limite=hoy+timedelta(days=(i%7)-2)), 'tarea','tareas',nombre)
                if i < 18:
                    etapa = 'Ganada' if i==14 else 'Perdida' if i==17 else ['Contacto','Visita','Oferta','Negociación'][i%4]
                    oportunidad = agregar(models.Oportunidad(lead_id=lead.id,propiedad_id=propiedad.id,
                        ejecutivo_id=responsable.id if responsable else None,tipo_operacion=propiedad.tipo_operacion,
                        etapa=etapa,valor_estimado=propiedad.precio,moneda=propiedad.moneda,
                        probabilidad=100 if etapa=='Ganada' else 0 if etapa=='Perdida' else 10+i%4*20,
                        fecha_cierre=hoy-timedelta(days=1) if cerrado else None,
                        motivo_cierre='Cierre ficticio del escenario de pruebas' if cerrado else None),
                        'oportunidad','oportunidades',nombre)
                    if i < 6 and propiedad.estado=='Disponible':
                        agregar(models.Visita(lead_id=lead.id,propiedad_id=propiedad.id,oportunidad_id=oportunidad.id,
                            ejecutivo_id=responsable.id if responsable else None,
                            fecha_hora=(ahora+timedelta(days=i+1)).replace(hour=14+i,minute=0,second=0,microsecond=0),
                            duracion_minutos=45,estado='Programada',modalidad='Presencial',
                            punto_encuentro=propiedad.direccion,proxima_accion='Confirmar asistencia'),
                            'visita','visitas',nombre)
            db.commit()
        except Exception:
            db.rollback()
            raise
    return cuentas


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true')
    args = parser.parse_args()
    if not args.aplicar:
        print('Escenario ficticio: 24 clientes, 18 propiedades y actividad comercial vinculada. Sin cambios.')
    else:
        try:
            print('Nuevos registros ficticios:', cargar())
        except Exception:
            print('No se completó la carga; los cambios de esta ejecución se revirtieron. Revisa el esquema y las colisiones de identificadores.')
            raise SystemExit(1)

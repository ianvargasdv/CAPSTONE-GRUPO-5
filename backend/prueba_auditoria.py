"""
Prueba de cobertura del registro de auditoría.

Se ejecuta con:  python prueba_auditoria.py
Termina con código 0 si todo pasa y 1 si algo falla.

Esta prueba es la contraparte de una decisión de diseño: la auditoría se registra
llamando explícitamente a auditoria.registrar() en cada endpoint, en lugar de
detectarla automáticamente con un listener de SQLAlchemy. El registro explícito no
produce entradas falsas, pero se puede olvidar en un endpoint nuevo. Esta prueba
cubre ese riesgo recorriendo los trece endpoints de escritura y comprobando que
todos dejen rastro. Si mañana se agrega uno y no se audita, hay que agregarlo acá y
la falta salta a la vista.

Corre sobre una base SQLite temporal que crea y borra sola, así que no toca los
datos reales de Supabase, y reemplaza el proveedor de IA por uno falso para no
gastar créditos. Llama a las funciones de los endpoints directamente, pasándoles la
sesión y el usuario que en producción inyecta FastAPI.

Lo que verifica:
  1. Que los trece endpoints de escritura dejen un registro de auditoría
  2. Que el resumen de cambios describa solo los campos que cambiaron de verdad
  3. Que los filtros del listado funcionen y rechacen valores inválidos
  4. Que la paginación no repita ni pierda registros
  5. Que un ejecutivo no pueda entrar al listado y un admin sí
  6. Que una operación fallida no deje registro de algo que no pasó
"""

import os
import sys

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_auditoria.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

# Se define antes de importar: database.py crea el engine al importarse y load_dotenv
# no sobrescribe las variables que ya existen en el entorno
os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"

import inspect
from datetime import date, timedelta

from fastapi import HTTPException

import auditoria
import database
import ia
import main
import models
import schemas
import seguridad

fallos = []
verificaciones = 0


def revisar(condicion, descripcion):
    global verificaciones
    verificaciones += 1
    if condicion:
        print(f"  ok    {descripcion}")
    else:
        print(f"  FALLA {descripcion}")
        fallos.append(descripcion)


# ── Preparación ──

models.Base.metadata.create_all(bind=database.engine)
db = database.SessionLocal()

admin = models.Usuario(
    nombre="Admin Prueba",
    email="admin@prueba.local",
    password_hash=seguridad.hashear_password("clave-de-prueba"),
    rol=seguridad.ROL_ADMIN,
    activo=True,
)
ejecutivo = models.Usuario(
    nombre="Ejecutivo Prueba",
    email="ejecutivo@prueba.local",
    password_hash=seguridad.hashear_password("clave-de-prueba"),
    rol=seguridad.ROL_EJECUTIVO,
    activo=True,
)
db.add(admin)
db.add(ejecutivo)
db.commit()


def registros(accion=None, entidad=None):
    """Consulta el registro de auditoría por acción y entidad."""
    consulta = db.query(models.Auditoria)
    if accion:
        consulta = consulta.filter(models.Auditoria.accion == accion)
    if entidad:
        consulta = consulta.filter(models.Auditoria.entidad == entidad)
    return consulta.all()


def hay(accion, entidad):
    return len(registros(accion, entidad)) > 0


# ── 1. Cobertura de los endpoints de escritura ──

print("\n1. Cada endpoint de escritura deja registro")

lead = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Ana Soto", email="ana@correo.cl", telefono="+56911111111"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.CREAR, auditoria.LEAD), "crear_lead registra")

main.actualizar_lead(
    lead_id=lead.id,
    datos=schemas.LeadActualizar(estado="Contactado", prioridad="Alta"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.ACTUALIZAR, auditoria.LEAD), "actualizar_lead registra")

propiedad = main.crear_propiedad(
    propiedad=schemas.PropiedadCrear(
        titulo="Depto Providencia", precio=120000000, direccion="Av. Siempre Viva 742"
    ),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.CREAR, auditoria.PROPIEDAD), "crear_propiedad registra")

main.actualizar_propiedad(
    propiedad_id=propiedad.id,
    datos=schemas.PropiedadActualizar(estado="Reservada"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.ACTUALIZAR, auditoria.PROPIEDAD), "actualizar_propiedad registra")

oportunidad = main.crear_oportunidad(
    datos=schemas.OportunidadCrear(
        lead_id=lead.id, propiedad_id=propiedad.id, tipo_operacion="Compra",
        valor_estimado=120000000, moneda="CLP",
    ),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.CREAR, auditoria.OPORTUNIDAD), "crear_oportunidad registra")

main.actualizar_oportunidad(
    oportunidad_id=oportunidad.id,
    datos=schemas.OportunidadActualizar(etapa="Visita"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.ACTUALIZAR, auditoria.OPORTUNIDAD), "actualizar_oportunidad registra")

main.crear_interaccion(
    lead_id=lead.id,
    datos=schemas.InteraccionCrear(tipo="Llamada", notas="Pidió ver el departamento"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.CREAR, auditoria.INTERACCION), "crear_interaccion registra")

interes = main.crear_interes(
    lead_id=lead.id,
    datos=schemas.InteresCrear(propiedad_id=propiedad.id, nivel_interes="Alto"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.CREAR, auditoria.INTERES), "crear_interes registra")

tarea = main.crear_tarea(
    datos=schemas.TareaCrear(titulo="Coordinar visita", lead_id=lead.id, fecha_limite="2026-09-20"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.CREAR, auditoria.TAREA), "crear_tarea registra")

main.actualizar_tarea(
    tarea_id=tarea.id,
    datos=schemas.TareaActualizar(estado="Completada"),
    db=db,
    usuario=ejecutivo,
)
revisar(hay(auditoria.ACTUALIZAR, auditoria.TAREA), "actualizar_tarea registra")

main.eliminar_tarea(tarea_id=tarea.id, db=db, usuario=ejecutivo)
revisar(hay(auditoria.ELIMINAR, auditoria.TAREA), "eliminar_tarea registra")

main.eliminar_interes(interes_id=interes.id, db=db, usuario=ejecutivo)
revisar(hay(auditoria.ELIMINAR, auditoria.INTERES), "eliminar_interes registra")

main.eliminar_oportunidad(oportunidad_id=oportunidad.id, db=db, usuario=ejecutivo)
revisar(hay(auditoria.ELIMINAR, auditoria.OPORTUNIDAD), "eliminar_oportunidad registra")


# El proveedor de IA se reemplaza por uno falso: interesa comprobar que la
# generación queda registrada, no que el modelo responda
def generar_falso(ficha, tipo):
    return {
        "texto": f"Análisis falso de tipo {tipo}",
        "modelo": "modelo-de-prueba",
        "tokens_entrada": 500,
        "tokens_salida": 120,
        "costo_estimado_usd": 0.00011,
    }


ia.esta_configurada = lambda: True
ia.generar_analisis = generar_falso

main.crear_analisis(lead_id=lead.id, tipo="resumen", db=db, usuario=admin)
revisar(hay(auditoria.GENERAR, auditoria.ANALISIS), "crear_analisis registra")

detalle_analisis = registros(auditoria.GENERAR, auditoria.ANALISIS)[0].detalle
revisar(
    "modelo-de-prueba" in detalle_analisis and "0.000110 USD" in detalle_analisis,
    f"el registro del análisis guarda modelo y costo ({detalle_analisis})",
)

main.eliminar_propiedad(propiedad_id=propiedad.id, db=db, usuario=admin)
revisar(hay(auditoria.ELIMINAR, auditoria.PROPIEDAD), "eliminar_propiedad registra")

main.eliminar_lead(lead_id=lead.id, db=db, usuario=admin)
revisar(hay(auditoria.ELIMINAR, auditoria.LEAD), "eliminar_lead registra")

# La comprobación de fondo: ningún endpoint de escritura quedó sin auditar
esperados = {
    (auditoria.CREAR, auditoria.LEAD),
    (auditoria.ACTUALIZAR, auditoria.LEAD),
    (auditoria.ELIMINAR, auditoria.LEAD),
    (auditoria.CREAR, auditoria.PROPIEDAD),
    (auditoria.ACTUALIZAR, auditoria.PROPIEDAD),
    (auditoria.ELIMINAR, auditoria.PROPIEDAD),
    (auditoria.CREAR, auditoria.OPORTUNIDAD),
    (auditoria.ACTUALIZAR, auditoria.OPORTUNIDAD),
    (auditoria.ELIMINAR, auditoria.OPORTUNIDAD),
    (auditoria.CREAR, auditoria.INTERACCION),
    (auditoria.CREAR, auditoria.TAREA),
    (auditoria.ACTUALIZAR, auditoria.TAREA),
    (auditoria.ELIMINAR, auditoria.TAREA),
    (auditoria.CREAR, auditoria.INTERES),
    (auditoria.ELIMINAR, auditoria.INTERES),
    (auditoria.GENERAR, auditoria.ANALISIS),
}
obtenidos = {(r.accion, r.entidad) for r in registros()}
revisar(
    esperados.issubset(obtenidos),
    f"los 16 endpoints de escritura están cubiertos (faltan: {esperados - obtenidos})",
)

# Todo registro debe decir quién actuó, aunque el usuario se borre después
revisar(
    all(r.usuario_email for r in registros()),
    "todos los registros guardan el correo del usuario",
)


# ── 2. Resumen de cambios ──

print("\n2. El resumen describe solo lo que cambió")

cambio_lead = registros(auditoria.ACTUALIZAR, auditoria.LEAD)[0].detalle
revisar("estado: Nuevo -> Contactado" in cambio_lead, f"detecta el cambio de estado ({cambio_lead})")
revisar("prioridad: Media -> Alta" in cambio_lead, "detecta el cambio de prioridad")
revisar("nombre" not in cambio_lead, "no menciona campos que no cambiaron")

sin_cambios = auditoria.resumir_cambios({"estado": "Nuevo"}, {"estado": "Nuevo"})
revisar(sin_cambios == "sin cambios efectivos", "informa cuando no hubo cambios reales")

vacio = auditoria.resumir_cambios({"telefono": None}, {"telefono": "+56900000000"})
revisar("vacío -> +56900000000" in vacio, f"representa el valor nulo como vacío ({vacio})")

# Guardar sin modificar nada tiene que quedar registrado igual: es información
lead2 = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Luis Pérez", email="luis@correo.cl"),
    db=db,
    usuario=ejecutivo,
)
main.actualizar_lead(
    lead_id=lead2.id,
    datos=schemas.LeadActualizar(nombre="Luis Pérez"),
    db=db,
    usuario=ejecutivo,
)
# Se ordena por id descendente para tomar el último: SQLite reutiliza los ids de
# las filas borradas, así que filtrar solo por entidad_id puede traer otro registro
ultimo = (
    db.query(models.Auditoria)
    .filter(
        models.Auditoria.accion == auditoria.ACTUALIZAR,
        models.Auditoria.entidad == auditoria.LEAD,
    )
    .order_by(models.Auditoria.id.desc())
    .first()
)
revisar(
    ultimo.detalle == "sin cambios efectivos",
    f"una actualización sin cambios queda registrada ({ultimo.detalle})",
)


# ── 3. Filtros del listado ──

print("\n3. Filtros del listado")


def listar(**filtros):
    """
    Envoltorio del endpoint del listado.

    Al llamar la función directamente, los parámetros de paginación llegan como
    objetos Query en lugar de números, porque es FastAPI quien los resuelve a partir
    de la URL. Se pasan explícitos y aparte se comprueba que los valores declarados
    por defecto sean los esperados.
    """
    filtros.setdefault("pagina", 1)
    filtros.setdefault("por_pagina", 25)
    return main.listar_auditoria(db=db, _admin=admin, **filtros)


firma = inspect.signature(main.listar_auditoria).parameters
revisar(firma["pagina"].default.default == 1, "la página por defecto es la primera")
revisar(firma["por_pagina"].default.default == 25, "el tamaño de página por defecto es 25")
# Las cotas quedan en metadata como objetos de annotated_types, no como atributos
restricciones = {type(m).__name__: m for m in firma["por_pagina"].default.metadata}
revisar(restricciones["Le"].le == 100, "el tope por página es 100")
revisar(restricciones["Ge"].ge == 1, "no se acepta un tamaño de página menor que 1")

cotas_pagina = {type(m).__name__: m for m in firma["pagina"].default.metadata}
revisar(cotas_pagina["Ge"].ge == 1, "no se aceptan páginas menores que 1")

todo = listar()
revisar(todo.total == len(registros()), f"el total coincide con la tabla ({todo.total})")

solo_leads = listar(entidad=auditoria.LEAD)
revisar(
    all(r.entidad == auditoria.LEAD for r in solo_leads.registros) and solo_leads.total > 0,
    f"filtra por entidad ({solo_leads.total} registros de lead)",
)

solo_eliminar = listar(accion=auditoria.ELIMINAR)
revisar(
    all(r.accion == auditoria.ELIMINAR for r in solo_eliminar.registros) and solo_eliminar.total > 0,
    f"filtra por acción ({solo_eliminar.total} eliminaciones)",
)

por_usuario = listar(usuario_email=admin.email)
revisar(
    all(r.usuario_email == admin.email for r in por_usuario.registros) and por_usuario.total > 0,
    f"filtra por usuario ({por_usuario.total} acciones del admin)",
)

busqueda = listar(busqueda="Ana Soto")
revisar(
    busqueda.total > 0 and all("Ana Soto" in r.descripcion for r in busqueda.registros),
    f"busca texto en la descripción ({busqueda.total} coincidencias)",
)

sin_resultado = listar(busqueda="texto que no existe")
revisar(sin_resultado.total == 0 and sin_resultado.registros == [], "una búsqueda sin coincidencias devuelve vacío")

hoy = date.today()
de_hoy = listar(desde=hoy.isoformat(), hasta=hoy.isoformat())
revisar(de_hoy.total == todo.total, f"el rango de hoy incluye el día completo ({de_hoy.total})")

anterior = (hoy - timedelta(days=2)).isoformat()
viejo = listar(desde=anterior, hasta=anterior)
revisar(viejo.total == 0, "un día sin actividad devuelve vacío")

futuro = listar(desde=(hoy + timedelta(days=1)).isoformat())
revisar(futuro.total == 0, "desde mañana no devuelve lo de hoy")

combinado = listar(entidad=auditoria.LEAD, accion=auditoria.CREAR, usuario_email=ejecutivo.email)
revisar(
    combinado.total == 2
    and all(
        r.entidad == auditoria.LEAD and r.accion == auditoria.CREAR and r.usuario_email == ejecutivo.email
        for r in combinado.registros
    ),
    f"los filtros se combinan ({combinado.total} leads creados por el ejecutivo)",
)

try:
    listar(entidad="inventada")
    revisar(False, "una entidad inválida devuelve 400")
except HTTPException as error:
    revisar(error.status_code == 400, f"una entidad inválida devuelve 400 ({error.detail})")

try:
    listar(accion="inventada")
    revisar(False, "una acción inválida devuelve 400")
except HTTPException as error:
    revisar(error.status_code == 400, "una acción inválida devuelve 400")

try:
    listar(desde="20-09-2026")
    revisar(False, "una fecha mal formada devuelve 400")
except HTTPException as error:
    revisar(error.status_code == 400, f"una fecha mal formada devuelve 400 ({error.detail})")


# ── 4. Paginación ──

print("\n4. Paginación")

total = todo.total
primera = listar(pagina=1, por_pagina=3)
revisar(len(primera.registros) == 3, "la primera página trae la cantidad pedida")
revisar(primera.total == total, "el total no cambia al paginar")

esperadas = (total + 2) // 3
revisar(primera.total_paginas == esperadas, f"calcula el total de páginas ({primera.total_paginas} para {total})")

segunda = listar(pagina=2, por_pagina=3)
ids_primera = {r.id for r in primera.registros}
ids_segunda = {r.id for r in segunda.registros}
revisar(not (ids_primera & ids_segunda), "las páginas no repiten registros")

vistos = set()
for numero in range(1, esperadas + 1):
    vistos.update(r.id for r in listar(pagina=numero, por_pagina=3).registros)
revisar(len(vistos) == total, f"recorriendo las páginas se ven todos los registros ({len(vistos)}/{total})")

ultima = listar(pagina=esperadas, por_pagina=3)
revisar(0 < len(ultima.registros) <= 3, "la última página no viene vacía")

fuera = listar(pagina=esperadas + 5, por_pagina=3)
revisar(fuera.registros == [] and fuera.total == total, "una página fuera de rango devuelve vacío sin error")

fechas = [r.fecha_creacion for r in listar(por_pagina=100).registros]
revisar(fechas == sorted(fechas, reverse=True), "los registros vienen del más reciente al más antiguo")


# ── 5. Acceso por rol ──

print("\n5. Acceso por rol")

try:
    seguridad.solo_admin(usuario=ejecutivo)
    revisar(False, "un ejecutivo no puede entrar al registro")
except HTTPException as error:
    revisar(error.status_code == 403, f"un ejecutivo recibe 403 y no 401 ({error.status_code})")

revisar(seguridad.solo_admin(usuario=admin) is admin, "un admin sí puede entrar")

opciones = main.filtros_auditoria(db=db, _admin=admin)
revisar(
    set(opciones.entidades) == set(auditoria.ENTIDADES),
    "los filtros ofrecen todas las entidades auditadas",
)
revisar(set(opciones.acciones) == set(auditoria.ACCIONES), "los filtros ofrecen todas las acciones")
revisar(
    set(opciones.usuarios) == {admin.email, ejecutivo.email},
    f"los filtros listan a los usuarios que actuaron ({opciones.usuarios})",
)


# ── 6. Atomicidad ──

print("\n6. La acción y su registro van juntos")

antes_de_fallar = len(registros())
try:
    main.actualizar_lead(
        lead_id=99999,
        datos=schemas.LeadActualizar(estado="Contactado"),
        db=db,
        usuario=ejecutivo,
    )
    revisar(False, "actualizar un lead inexistente devuelve 404")
except HTTPException as error:
    revisar(error.status_code == 404, "actualizar un lead inexistente devuelve 404")

revisar(len(registros()) == antes_de_fallar, "una operación fallida no deja registro")


# ── Cierre ──

db.close()
database.engine.dispose()
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

print("\n" + "-" * 60)
if fallos:
    print(f"{len(fallos)} de {verificaciones} verificaciones fallaron:")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)

print(f"Las {verificaciones} verificaciones pasaron")

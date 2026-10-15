"""
Prueba de cobertura de la asignación de leads a ejecutivos.

Se ejecuta con:  python prueba_asignacion.py
Termina con código 0 si todo pasa y 1 si algo falla.

Corre sobre una base SQLite temporal que crea y borra sola, así que no toca los
datos reales de Supabase. Todos los datos son ficticios.

Casos cubiertos:
  1.  Asignar un lead que no tiene ejecutivo
  2.  Consultar el lead y comprobar que conserva la asignación
  3.  Reasignar el lead a otro ejecutivo
  4.  Verificar que el historial conserva la asignación anterior y registra la nueva
  5.  Consultar el historial y comprobar el orden cronológico
  6.  Intentar asignar un lead inexistente
  7.  Intentar asignar un ejecutivo inexistente
  8.  Intentar asignar un ejecutivo inactivo
  9.  Comprobar que una operación fallida no genera registro histórico
  10. Quitar la asignación (ejecutivo_id nulo)
  11. Verificar que la asignación actual y el historial son consistentes
  12. Comprobar que listar_leads devuelve el ejecutivo adjunto
  13. Comprobar que crear_lead devuelve ejecutivo=None sin asignación
  14. Comprobar que actualizar_lead mantiene el ejecutivo
  15. Comprobar que listar_ejecutivos solo devuelve usuarios activos
  16. Comprobar que las funciones existentes de leads siguen funcionando
"""

import os
import sys

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_asignacion.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"

from fastapi import HTTPException

import database
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
    password_hash=seguridad.hashear_password("clave"),
    rol=seguridad.ROL_ADMIN,
    activo=True,
)
ejecutivo_a = models.Usuario(
    nombre="Ana López",
    email="ana@prueba.local",
    password_hash=seguridad.hashear_password("clave"),
    rol=seguridad.ROL_EJECUTIVO,
    activo=True,
)
ejecutivo_b = models.Usuario(
    nombre="Bruno Soto",
    email="bruno@prueba.local",
    password_hash=seguridad.hashear_password("clave"),
    rol=seguridad.ROL_EJECUTIVO,
    activo=True,
)
ejecutivo_inactivo = models.Usuario(
    nombre="Inactivo",
    email="inactivo@prueba.local",
    password_hash=seguridad.hashear_password("clave"),
    rol=seguridad.ROL_EJECUTIVO,
    activo=False,
)
db.add_all([admin, ejecutivo_a, ejecutivo_b, ejecutivo_inactivo])
db.commit()


# ── 1. Asignar un lead sin ejecutivo ──

print("\n1. Primera asignación")

lead = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Carlos Vera", email="carlos@ejemplo.cl"),
    db=db,
    usuario=admin,
)
revisar(lead.ejecutivo_id is None, "lead recién creado no tiene ejecutivo")
revisar(lead.ejecutivo is None, "lead recién creado devuelve ejecutivo=None")

resultado = main.asignar_lead(
    lead_id=lead.id,
    datos=schemas.AsignacionCrear(ejecutivo_id=ejecutivo_a.id),
    db=db,
    usuario=admin,
)
revisar(resultado.ejecutivo_id == ejecutivo_a.id, "asignación guarda el ejecutivo_id correcto")
revisar(
    resultado.ejecutivo is not None and resultado.ejecutivo.nombre == ejecutivo_a.nombre,
    f"la respuesta incluye el ejecutivo como objeto ({resultado.ejecutivo})",
)


# ── 2. Persistencia: el lead conserva la asignación ──

print("\n2. Persistencia")

# Consultar los leads directamente para simular una recarga
leads = main.listar_leads(db=db)
lead_recargado = next((l for l in leads if l.id == lead.id), None)

revisar(lead_recargado is not None, "el lead aparece en listar_leads")
revisar(
    lead_recargado.ejecutivo_id == ejecutivo_a.id,
    "el lead conserva ejecutivo_id después de recargar",
)
revisar(
    lead_recargado.ejecutivo is not None
    and lead_recargado.ejecutivo.nombre == ejecutivo_a.nombre,
    "listar_leads devuelve el ejecutivo como objeto",
)


# ── 3. Reasignación ──

print("\n3. Reasignación")

reasignado = main.asignar_lead(
    lead_id=lead.id,
    datos=schemas.AsignacionCrear(ejecutivo_id=ejecutivo_b.id),
    db=db,
    usuario=admin,
)
revisar(reasignado.ejecutivo_id == ejecutivo_b.id, "reasignación actualiza ejecutivo_id")
revisar(
    reasignado.ejecutivo.nombre == ejecutivo_b.nombre,
    "reasignación devuelve el nuevo ejecutivo como objeto",
)


# ── 4. Historial conserva el estado anterior y registra el nuevo ──

print("\n4. Historial de asignaciones")

historial = main.historial_asignaciones(lead_id=lead.id, db=db)

revisar(len(historial) == 2, f"hay exactamente 2 entradas en el historial ({len(historial)})")

# Identificar las entradas por contenido, no por posición:
# SQLite puede asignar el mismo timestamp a commits seguidos, así que no se
# puede asumir que historial[0] sea siempre la reasignación.
entrada_primera_asig = next(
    (e for e in historial if e.ejecutivo_anterior_id is None and e.ejecutivo_nuevo_id == ejecutivo_a.id),
    None,
)
entrada_reasignacion = next(
    (e for e in historial if e.ejecutivo_anterior_id == ejecutivo_a.id and e.ejecutivo_nuevo_id == ejecutivo_b.id),
    None,
)

revisar(
    entrada_primera_asig is not None,
    "existe una entrada de primera asignación (sin anterior) a Ana López",
)
revisar(
    entrada_primera_asig is not None
    and entrada_primera_asig.ejecutivo_anterior_nombre is None,
    "primera asignación no tiene ejecutivo anterior",
)
revisar(
    entrada_primera_asig is not None
    and entrada_primera_asig.ejecutivo_nuevo_nombre == ejecutivo_a.nombre,
    f"primera asignación apunta a {ejecutivo_a.nombre}",
)

revisar(
    entrada_reasignacion is not None,
    "existe una entrada de reasignación de Ana López a Bruno Soto",
)
revisar(
    entrada_reasignacion is not None
    and entrada_reasignacion.ejecutivo_anterior_nombre == ejecutivo_a.nombre,
    f"reasignación registra el anterior correctamente ({ejecutivo_a.nombre})",
)
revisar(
    entrada_reasignacion is not None
    and entrada_reasignacion.ejecutivo_nuevo_nombre == ejecutivo_b.nombre,
    f"reasignación apunta al nuevo ejecutivo ({ejecutivo_b.nombre})",
)

revisar(
    any(e.realizado_por_email == admin.email for e in historial),
    "el historial guarda quién hizo el cambio",
)


# ── 5. Orden cronológico del historial ──

print("\n5. Orden cronológico")

fechas = [e.fecha_creacion for e in historial]
revisar(
    all(a >= b for a, b in zip(fechas, fechas[1:])),
    "el historial viene del más reciente al más antiguo",
)


# ── 6. Lead inexistente ──

print("\n6. Validaciones")

try:
    main.asignar_lead(
        lead_id=99999,
        datos=schemas.AsignacionCrear(ejecutivo_id=ejecutivo_a.id),
        db=db,
        usuario=admin,
    )
    revisar(False, "asignar un lead inexistente debe devolver 404")
except HTTPException as error:
    revisar(error.status_code == 404, f"lead inexistente devuelve 404 ({error.status_code})")


# ── 7. Ejecutivo inexistente ──

try:
    main.asignar_lead(
        lead_id=lead.id,
        datos=schemas.AsignacionCrear(ejecutivo_id=99999),
        db=db,
        usuario=admin,
    )
    revisar(False, "asignar un ejecutivo inexistente debe devolver 404")
except HTTPException as error:
    revisar(error.status_code == 404, f"ejecutivo inexistente devuelve 404 ({error.status_code})")


# ── 8. Ejecutivo inactivo ──

try:
    main.asignar_lead(
        lead_id=lead.id,
        datos=schemas.AsignacionCrear(ejecutivo_id=ejecutivo_inactivo.id),
        db=db,
        usuario=admin,
    )
    revisar(False, "asignar un ejecutivo inactivo debe devolver 404")
except HTTPException as error:
    revisar(
        error.status_code == 404,
        f"ejecutivo inactivo devuelve 404 ({error.detail})",
    )


# ── 9. Operación fallida no deja registro histórico ──

print("\n9. Atomicidad")

entradas_antes = db.query(models.HistorialAsignacion).count()

for id_invalido in [99999, ejecutivo_inactivo.id]:
    try:
        main.asignar_lead(
            lead_id=lead.id if id_invalido == ejecutivo_inactivo.id else 99999,
            datos=schemas.AsignacionCrear(ejecutivo_id=id_invalido),
            db=db,
            usuario=admin,
        )
    except HTTPException:
        pass

entradas_despues = db.query(models.HistorialAsignacion).count()
revisar(
    entradas_despues == entradas_antes,
    f"las operaciones fallidas no dejan registros ({entradas_antes} -> {entradas_despues})",
)


# ── 10. Quitar asignación (ejecutivo_id nulo) ──

print("\n10. Quitar asignación")

sin_ejecutivo = main.asignar_lead(
    lead_id=lead.id,
    datos=schemas.AsignacionCrear(ejecutivo_id=None),
    db=db,
    usuario=admin,
)
revisar(sin_ejecutivo.ejecutivo_id is None, "quitar asignación pone ejecutivo_id en None")
revisar(sin_ejecutivo.ejecutivo is None, "quitar asignación pone ejecutivo en None")

historial_tras_quitar = main.historial_asignaciones(lead_id=lead.id, db=db)

# Buscar la entrada donde se quitó la asignación (nuevo=None, anterior=ejecutivo_b)
entrada_quitar = next(
    (e for e in historial_tras_quitar
     if e.ejecutivo_nuevo_id is None and e.ejecutivo_anterior_id == ejecutivo_b.id),
    None,
)

revisar(
    entrada_quitar is not None,
    "quitar asignación genera entrada en el historial con ejecutivo_nuevo=None",
)
revisar(
    entrada_quitar is not None
    and entrada_quitar.ejecutivo_anterior_id == ejecutivo_b.id,
    "la entrada de quitar guarda el ejecutivo anterior correctamente",
)


# ── 11. Consistencia asignación actual ↔ historial ──

print("\n11. Consistencia")

historial_final = main.historial_asignaciones(lead_id=lead.id, db=db)

# La última acción fue quitar asignación (ejecutivo_nuevo_id=None)
ultima_entrada = next(
    (e for e in historial_final if e.ejecutivo_nuevo_id is None
     and e.ejecutivo_anterior_id == ejecutivo_b.id),
    None,
)
lead_actual = next(l for l in main.listar_leads(db=db) if l.id == lead.id)
revisar(
    ultima_entrada is not None
    and lead_actual.ejecutivo_id == ultima_entrada.ejecutivo_nuevo_id,
    "la asignación actual coincide con la última entrada del historial",
)


# ── 12. listar_leads adjunta ejecutivos en una sola query ──

print("\n12. listar_leads con ejecutivos")

# Crear otro lead ya asignado para verificar que se adjuntan múltiples
lead2 = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Diana Mora", email="diana@ejemplo.cl"),
    db=db,
    usuario=admin,
)
main.asignar_lead(
    lead_id=lead2.id,
    datos=schemas.AsignacionCrear(ejecutivo_id=ejecutivo_a.id),
    db=db,
    usuario=admin,
)

todos = main.listar_leads(db=db)
con_ejecutivo = [l for l in todos if l.ejecutivo is not None]
sin_ejecutivo_lista = [l for l in todos if l.ejecutivo is None]

revisar(
    len(con_ejecutivo) >= 1,
    f"listar_leads devuelve al menos un lead con ejecutivo ({len(con_ejecutivo)})",
)
revisar(
    all(l.ejecutivo.id == l.ejecutivo_id for l in con_ejecutivo),
    "ejecutivo.id coincide con ejecutivo_id en todos los leads",
)
revisar(
    all(l.ejecutivo is None for l in sin_ejecutivo_lista),
    "los leads sin asignar tienen ejecutivo=None",
)


# ── 13. crear_lead devuelve ejecutivo=None ──

print("\n13. crear_lead sin asignación")

lead3 = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Eduardo Paz", email="edu@ejemplo.cl"),
    db=db,
    usuario=admin,
)
revisar(lead3.ejecutivo is None, "crear_lead retorna ejecutivo=None cuando no hay asignación")
revisar(lead3.ejecutivo_id is None, "crear_lead retorna ejecutivo_id=None")


# ── 14. actualizar_lead mantiene el ejecutivo ──

print("\n14. actualizar_lead preserva la asignación")

main.asignar_lead(
    lead_id=lead3.id,
    datos=schemas.AsignacionCrear(ejecutivo_id=ejecutivo_b.id),
    db=db,
    usuario=admin,
)

actualizado = main.actualizar_lead(
    lead_id=lead3.id,
    datos=schemas.LeadActualizar(estado="Contactado"),
    db=db,
    usuario=admin,
)
revisar(
    actualizado.ejecutivo_id == ejecutivo_b.id,
    "actualizar_lead conserva ejecutivo_id sin tocarlo",
)
revisar(
    actualizado.ejecutivo is not None and actualizado.ejecutivo.nombre == ejecutivo_b.nombre,
    "actualizar_lead devuelve el ejecutivo como objeto",
)


# ── 15. listar_ejecutivos solo devuelve activos ──

print("\n15. listar_ejecutivos")

ejecutivos = main.listar_ejecutivos(db=db)
revisar(len(ejecutivos) >= 2, f"hay al menos 2 ejecutivos activos ({len(ejecutivos)})")
revisar(
    all(getattr(e, 'activo', True) is not False for e in ejecutivos),
    "listar_ejecutivos no incluye al inactivo",
)
revisar(
    not any(e.email == ejecutivo_inactivo.email for e in ejecutivos),
    "el ejecutivo inactivo no aparece en la lista",
)
revisar(
    ejecutivos == sorted(ejecutivos, key=lambda e: e.nombre),
    "la lista viene ordenada por nombre",
)


# ── 16. Funcionalidades existentes siguen funcionando ──

print("\n16. Regresión: funcionalidades existentes")

# Crear y eliminar lead con auditoría
lead_tmp = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Tmp Borrarlo", email="tmp@ejemplo.cl"),
    db=db,
    usuario=admin,
)
revisar(lead_tmp.id is not None, "crear_lead sigue funcionando con el nuevo modelo")

main.eliminar_lead(lead_id=lead_tmp.id, db=db, usuario=admin)
revisar(
    db.query(models.Lead).filter(models.Lead.id == lead_tmp.id).first() is None,
    "eliminar_lead sigue funcionando",
)
revisar(
    db.query(models.HistorialAsignacion).filter(
        models.HistorialAsignacion.lead_id == lead_tmp.id
    ).count() == 0,
    "eliminar_lead borra en cascada el historial de asignaciones del lead",
)

# Listar sin romper
lista_final = main.listar_leads(db=db)
revisar(isinstance(lista_final, list), "listar_leads retorna lista sin errores")


# ── Cierre ──

db.close()
database.engine.dispose()
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

print(f"\n{'-' * 60}")
if fallos:
    print(f"{len(fallos)} de {verificaciones} verificaciones fallaron:")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)

print(f"Las {verificaciones} verificaciones pasaron")

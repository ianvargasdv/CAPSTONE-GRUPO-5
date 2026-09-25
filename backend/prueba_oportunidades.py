"""Pruebas de negocio del pipeline sobre una base SQLite temporal."""

import os

from pydantic import ValidationError

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_oportunidades.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)
os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"
os.environ["SECRET_KEY"] = "clave-temporal-solo-pruebas-32-bytes-minimo"

from fastapi import HTTPException

import database
import auditoria
import main
import models
import schemas
import seguridad


fallos = []
verificaciones = 0


def revisar(condicion, descripcion):
    global verificaciones
    verificaciones += 1
    print(f"  {'ok   ' if condicion else 'FALLA'} {descripcion}")
    if not condicion:
        fallos.append(descripcion)


models.Base.metadata.create_all(bind=database.engine)
db = database.SessionLocal()
usuario = models.Usuario(
    nombre="Ejecutiva Pipeline", email="pipeline@prueba.local",
    password_hash=seguridad.hashear_password("clave-de-prueba"), activo=True,
)
lead = models.Lead(nombre="Lead Pipeline", email="lead@prueba.local")
propiedad = models.Propiedad(
    titulo="Departamento Prueba", tipo="Departamento", precio=100000000,
    direccion="Dirección de prueba", estado="Disponible",
)
db.add_all([usuario, lead, propiedad])
db.commit()
db.refresh(usuario)
db.refresh(lead)
db.refresh(propiedad)

print("\n1. Creación y valores por etapa")
oportunidad = main.crear_oportunidad(
    datos=schemas.OportunidadCrear(
        lead_id=lead.id, propiedad_id=propiedad.id, tipo_operacion="Compra",
        valor_estimado=105000000, moneda="CLP",
    ),
    db=db,
    usuario=usuario,
)
revisar(oportunidad.etapa == "Contacto" and oportunidad.probabilidad == 10,
        "una oportunidad parte en Contacto con 10%")
revisar(oportunidad.lead_nombre == lead.nombre and oportunidad.propiedad_titulo == propiedad.titulo,
        "la respuesta incluye los nombres relacionados")
revisar(oportunidad.ejecutivo_id == usuario.id and oportunidad.ejecutivo_nombre == usuario.nombre,
        "queda asignada al ejecutivo que la creó")
ficha = main.ia.construir_ficha(lead, [], [], {}, [], [oportunidad])
revisar("OPORTUNIDADES COMERCIALES" in ficha and "105000000 CLP" in ficha,
        "la IA recibe el negocio y su valor como contexto")

print("\n2. Validaciones")
try:
    schemas.OportunidadCrear(
        lead_id=lead.id, tipo_operacion="Compra", valor_estimado=1000,
    )
except ValidationError:
    revisar(True, "un valor estimado exige moneda")
else:
    revisar(False, "un valor estimado exige moneda")

try:
    schemas.OportunidadCrear(
        lead_id=lead.id, tipo_operacion="Compra", etapa="Perdida",
    )
except ValidationError:
    revisar(True, "una pérdida exige motivo")
else:
    revisar(False, "una pérdida exige motivo")

try:
    main.crear_oportunidad(
        datos=schemas.OportunidadCrear(lead_id=99999, tipo_operacion="Compra"),
        db=db, usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 404, "rechaza un lead inexistente")
else:
    revisar(False, "rechaza un lead inexistente")

print("\n3. Movimiento y cierre")
oportunidad = main.actualizar_oportunidad(
    oportunidad_id=oportunidad.id,
    datos=schemas.OportunidadActualizar(etapa="Negociación"),
    db=db, usuario=usuario,
)
revisar(oportunidad.probabilidad == 80 and oportunidad.fecha_cierre is None,
        "Negociación ajusta la probabilidad a 80%")

try:
    main.actualizar_oportunidad(
        oportunidad_id=oportunidad.id,
        datos=schemas.OportunidadActualizar(etapa="Perdida"),
        db=db, usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 422, "no permite cerrar como perdida sin motivo")
else:
    revisar(False, "no permite cerrar como perdida sin motivo")

oportunidad = main.actualizar_oportunidad(
    oportunidad_id=oportunidad.id,
    datos=schemas.OportunidadActualizar(etapa="Perdida", motivo_cierre="Eligió otra propiedad"),
    db=db, usuario=usuario,
)
revisar(oportunidad.probabilidad == 0 and oportunidad.fecha_cierre is not None,
        "una pérdida queda cerrada con probabilidad 0% y fecha")

oportunidad = main.actualizar_oportunidad(
    oportunidad_id=oportunidad.id,
    datos=schemas.OportunidadActualizar(etapa="Visita"),
    db=db, usuario=usuario,
)
revisar(oportunidad.probabilidad == 30 and oportunidad.fecha_cierre is None,
        "reabrir devuelve la probabilidad de etapa y limpia la fecha")
revisar(oportunidad.motivo_cierre is None, "reabrir limpia el motivo de pérdida")

print("\n4. Listado y borrado")
listado = main.listar_oportunidades(db=db)
revisar(len(listado) == 1 and listado[0].id == oportunidad.id,
        "el listado devuelve la oportunidad enriquecida")
main.eliminar_oportunidad(oportunidad_id=oportunidad.id, db=db, usuario=usuario)
revisar(db.query(models.Oportunidad).count() == 0, "elimina la oportunidad")
revisar(db.query(models.Auditoria).filter(models.Auditoria.entidad == auditoria.OPORTUNIDAD).count() >= 5,
        "creación, movimientos y eliminación quedan auditados")

db.close()
database.engine.dispose()
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

print("\n" + "-" * 60)
if fallos:
    print(f"{len(fallos)} de {verificaciones} verificaciones fallaron")
    raise SystemExit(1)
print(f"Las {verificaciones} verificaciones pasaron")

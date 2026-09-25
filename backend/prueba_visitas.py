"""Pruebas de negocio de la agenda sobre una base SQLite temporal."""

import os
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_visitas.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)
os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"
os.environ["SECRET_KEY"] = "clave-temporal-solo-pruebas-32-bytes-minimo"

from fastapi import HTTPException

import auditoria
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
    print(f"  {'ok   ' if condicion else 'FALLA'} {descripcion}")
    if not condicion:
        fallos.append(descripcion)


models.Base.metadata.create_all(bind=database.engine)
db = database.SessionLocal()
usuario = models.Usuario(
    nombre="Ejecutiva Agenda", email="agenda@prueba.local",
    password_hash=seguridad.hashear_password("clave-de-prueba"), activo=True,
)
lead = models.Lead(nombre="Lead Agenda", email="lead-agenda@prueba.local")
propiedad = models.Propiedad(
    titulo="Departamento Agenda", tipo="Departamento", precio=100000000,
    direccion="Dirección de agenda", estado="Disponible",
)
otra_propiedad = models.Propiedad(
    titulo="Casa Agenda", tipo="Casa", precio=160000000,
    direccion="Otra dirección", estado="Disponible",
)
db.add_all([usuario, lead, propiedad, otra_propiedad])
db.commit()
for registro in (usuario, lead, propiedad, otra_propiedad):
    db.refresh(registro)

oportunidad = main.crear_oportunidad(
    datos=schemas.OportunidadCrear(
        lead_id=lead.id, propiedad_id=propiedad.id, tipo_operacion="Compra"
    ),
    db=db, usuario=usuario,
)
inicio = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=1)

print("\n1. Creación y contexto")
visita = main.crear_visita(
    datos=schemas.VisitaCrear(
        lead_id=lead.id, propiedad_id=propiedad.id, oportunidad_id=oportunidad.id,
        fecha_hora=inicio, duracion_minutos=60, punto_encuentro=propiedad.direccion,
    ),
    db=db, usuario=usuario,
)
revisar(visita.estado == "Programada" and visita.ejecutivo_id == usuario.id,
        "la visita queda programada y asignada al ejecutivo")
revisar(visita.lead_nombre == lead.nombre and visita.propiedad_titulo == propiedad.titulo,
        "la respuesta incluye lead y propiedad")
ficha = main.ia.construir_ficha(lead, [], [], {}, [], [], [visita])
revisar("AGENDA Y RESULTADOS DE VISITAS" in ficha and propiedad.titulo in ficha,
        "la IA recibe la agenda como contexto verificable")

print("\n2. Validaciones")
for datos, descripcion in [
    ({"fecha_hora": datetime.now()}, "exige zona horaria"),
    ({"fecha_hora": inicio, "estado": "Realizada"}, "una visita realizada exige resultado"),
    ({"fecha_hora": inicio, "estado": "Cancelada"}, "una cancelación exige motivo"),
]:
    try:
        schemas.VisitaCrear(lead_id=lead.id, propiedad_id=propiedad.id, **datos)
    except ValidationError:
        revisar(True, descripcion)
    else:
        revisar(False, descripcion)

try:
    main.crear_visita(
        datos=schemas.VisitaCrear(
            lead_id=lead.id, propiedad_id=otra_propiedad.id,
            oportunidad_id=oportunidad.id, fecha_hora=inicio + timedelta(days=2),
        ),
        db=db, usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 422, "rechaza una oportunidad de otra propiedad")
else:
    revisar(False, "rechaza una oportunidad de otra propiedad")

try:
    main.crear_visita(
        datos=schemas.VisitaCrear(
            lead_id=lead.id, propiedad_id=propiedad.id,
            fecha_hora=inicio + timedelta(minutes=30), duracion_minutos=30,
        ),
        db=db, usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 409, "impide horarios que se cruzan para el ejecutivo")
else:
    revisar(False, "impide horarios que se cruzan para el ejecutivo")

adyacente = main.crear_visita(
    datos=schemas.VisitaCrear(
        lead_id=lead.id, propiedad_id=otra_propiedad.id,
        fecha_hora=inicio + timedelta(minutes=60), duracion_minutos=30,
    ),
    db=db, usuario=usuario,
)
revisar(adyacente.id is not None, "permite una visita inmediatamente después de otra")

print("\n3. Resultado, cancelación y disponibilidad")
try:
    main.actualizar_visita(
        visita_id=visita.id, datos=schemas.VisitaActualizar(estado="Realizada"),
        db=db, usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 422, "no permite marcar realizada sin registrar resultado")
else:
    revisar(False, "no permite marcar realizada sin registrar resultado")

visita = main.actualizar_visita(
    visita_id=visita.id,
    datos=schemas.VisitaActualizar(
        estado="Realizada", resultado="Solicitó una simulación de financiamiento"
    ),
    db=db, usuario=usuario,
)
revisar(visita.estado == "Realizada" and bool(visita.resultado),
        "guarda el resultado de la visita")

visita = main.actualizar_visita(
    visita_id=visita.id,
    datos=schemas.VisitaActualizar(
        estado="Cancelada", motivo_cancelacion="Reagendada por el cliente"
    ),
    db=db, usuario=usuario,
)
reemplazo = main.crear_visita(
    datos=schemas.VisitaCrear(
        lead_id=lead.id, propiedad_id=propiedad.id,
        fecha_hora=inicio, duracion_minutos=30,
    ),
    db=db, usuario=usuario,
)
revisar(reemplazo.id is not None, "una visita cancelada deja disponible su horario")

print("\n4. Listado, borrado y auditoría")
listado = main.listar_visitas(db=db)
revisar(len(listado) == 3 and [item.fecha_hora for item in listado] == sorted(
    item.fecha_hora for item in listado
), "el listado viene ordenado por fecha")
main.eliminar_visita(visita_id=reemplazo.id, db=db, usuario=usuario)
revisar(db.query(models.Visita).count() == 2, "elimina una visita")
revisar(
    db.query(models.Auditoria).filter(models.Auditoria.entidad == auditoria.VISITA).count() >= 6,
    "creación, cambios y eliminación quedan auditados",
)

db.close()
database.engine.dispose()
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

print("\n" + "-" * 60)
if fallos:
    print(f"{len(fallos)} de {verificaciones} verificaciones fallaron")
    raise SystemExit(1)
print(f"Las {verificaciones} verificaciones pasaron")

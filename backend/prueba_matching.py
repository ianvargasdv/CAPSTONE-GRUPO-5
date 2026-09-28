"""Pruebas del matching determinista sobre una base SQLite temporal."""

import os

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_matching.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)
os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"
os.environ["SECRET_KEY"] = "clave-temporal-solo-pruebas-32-bytes-minimo"

from fastapi import HTTPException

import database
import main
import matching
import models
import schemas


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
lead = models.Lead(
    nombre="Lead Matching", email="matching@prueba.local", tipo_operacion="Compra",
    presupuesto_min=140_000_000, presupuesto_max=180_000_000, moneda="CLP",
    comunas_interes="Ñuñoa, Macul", tipo_propiedad_buscada="Departamento",
    dormitorios_min=2, banos_min=2,
)
perfecta = models.Propiedad(
    titulo="Departamento compatible", tipo="Departamento", tipo_operacion="Compra",
    precio=165_000_000, moneda="CLP", direccion="Dirección 1", comuna="Nunoa",
    dormitorios=2, banos=2, estado="Disponible",
)
parcial = models.Propiedad(
    titulo="Casa fuera de perfil", tipo="Casa", tipo_operacion="Arriendo",
    precio=900_000, moneda="CLP", direccion="Dirección 2", comuna="Providencia",
    dormitorios=1, banos=1, estado="Disponible",
)
reservada = models.Propiedad(
    titulo="Compatible pero reservada", tipo="Departamento", tipo_operacion="Compra",
    precio=160_000_000, moneda="CLP", direccion="Dirección 3", comuna="Ñuñoa",
    dormitorios=2, banos=2, estado="Reservada",
)
incompleta = models.Propiedad(
    titulo="Ficha incompleta", tipo="Departamento", precio=150_000_000,
    direccion="Dirección 4", estado="Disponible",
)
db.add_all([lead, perfecta, parcial, reservada, incompleta])
db.commit()

print("\n1. Puntaje y explicaciones")
resultado = matching.calcular_matching(lead, perfecta)
revisar(resultado["puntaje"] == 100 and resultado["cobertura"] == 100,
        "una coincidencia completa obtiene 100% con cobertura total")
revisar(len(resultado["criterios"]) == 6 and all(c["coincide"] for c in resultado["criterios"]),
        "explica los seis criterios que sí coinciden")
revisar(resultado["categoria"] == "Excelente", "clasifica el resultado excelente")

resultado_parcial = matching.calcular_matching(lead, parcial)
revisar(resultado_parcial["puntaje"] == 0 and resultado_parcial["categoria"] == "Parcial",
        "los datos incompatibles no suman puntaje")
revisar(any("fuera" in c["detalle"] for c in resultado_parcial["criterios"]),
        "explica por qué el precio no coincide")

print("\n2. Datos faltantes y normalización")
resultado_incompleto = matching.calcular_matching(lead, incompleta)
revisar(resultado_incompleto["cobertura"] == 20,
        "la cobertura baja cuando faltan datos comparables")
revisar(resultado_incompleto["puntaje"] == 100 and resultado_incompleto["datos_faltantes"],
        "separa coincidencia de cobertura para no ocultar datos faltantes")
criterio_comuna = next(c for c in resultado["criterios"] if c["nombre"] == "Comuna")
revisar(criterio_comuna["coincide"], "compara comunas sin depender de tildes o mayúsculas")

print("\n3. Endpoint y disponibilidad")
listado = main.obtener_matching(lead_id=lead.id, db=db)
revisar([item["propiedad"].id for item in listado] == [perfecta.id, incompleta.id, parcial.id],
        "ordena por coincidencia y usa cobertura para desempatar")
revisar(all(item["propiedad"].id != reservada.id for item in listado),
        "excluye propiedades reservadas del resultado comercial")
for item in listado:
    schemas.MatchingPropiedadRespuesta.model_validate(item)
revisar(True, "la respuesta cumple el contrato de la API")
ficha = main.ia.construir_ficha(lead, [], [], {}, [], [], [], listado)
revisar("COINCIDENCIAS CALCULADAS" in ficha and "100% de coincidencia" in ficha,
        "la IA recibe el ranking calculado y su cobertura, sin recalcularlo")

try:
    main.obtener_matching(lead_id=99999, db=db)
except HTTPException as error:
    revisar(error.status_code == 404, "un lead inexistente devuelve 404")
else:
    revisar(False, "un lead inexistente devuelve 404")

db.close()
database.engine.dispose()
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

print("\n" + "-" * 60)
if fallos:
    print(f"{len(fallos)} de {verificaciones} verificaciones fallaron")
    raise SystemExit(1)
print(f"Las {verificaciones} verificaciones pasaron")

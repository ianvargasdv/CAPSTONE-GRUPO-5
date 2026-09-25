"""Pruebas de regresión para las reglas de entrada del CRM.

Se ejecuta con ``python prueba_validaciones.py``. Usa una base SQLite temporal:
no lee ni modifica los datos reales configurados en ``backend/.env``.
"""

import os

from pydantic import ValidationError

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_validaciones.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"
os.environ["SECRET_KEY"] = "clave-temporal-solo-pruebas-32-bytes-minimo"

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


def rechaza(constructor, descripcion):
    try:
        constructor()
    except ValidationError:
        revisar(True, descripcion)
    else:
        revisar(False, descripcion)


print("\n1. Normalización y casos válidos")

lead_valido = schemas.LeadCrear(
    nombre="  Ana Soto  ",
    email="  ANA@CORREO.CL  ",
    telefono="+56 9 1111 1111",
)
revisar(lead_valido.nombre == "Ana Soto", "el nombre elimina espacios exteriores")
revisar(lead_valido.email == "ana@correo.cl", "el correo se normaliza a minúsculas")
revisar(schemas.PropiedadCrear(titulo="Casa", precio=1, direccion="Santiago").precio == 1,
        "el precio mínimo válido es aceptado")
revisar(schemas.TareaCrear(titulo="Llamar", fecha_limite="2026-12-31").fecha_limite == "2026-12-31",
        "una fecha real en formato ISO es aceptada")
revisar(schemas.LeadActualizar(telefono=None).model_dump(exclude_unset=True) == {"telefono": None},
        "el teléfono se puede limpiar explícitamente")


print("\n2. Entradas inválidas y límites")

rechaza(lambda: schemas.LeadCrear(nombre="A", email="ana@correo.cl"),
        "rechaza nombres demasiado cortos")
rechaza(lambda: schemas.LeadCrear(nombre="Ana Soto", email="correo-sin-dominio"),
        "rechaza correos inválidos")
rechaza(lambda: schemas.LeadCrear(nombre="Ana Soto", email="ana@correo.cl", telefono="abc1234"),
        "rechaza teléfonos con letras")
rechaza(lambda: schemas.LeadCrear(nombre="Ana Soto", email="ana@correo.cl", estado="Dormido"),
        "rechaza estados de lead desconocidos")
rechaza(lambda: schemas.LeadActualizar(nombre=None),
        "no permite borrar un nombre obligatorio con null")
rechaza(lambda: schemas.PropiedadCrear(titulo="Casa", precio=0, direccion="Santiago"),
        "rechaza precios iguales a cero")
rechaza(lambda: schemas.PropiedadCrear(titulo="Casa", precio=100, direccion="Santiago", tipo="Bodega"),
        "rechaza tipos de propiedad desconocidos")
rechaza(lambda: schemas.PropiedadCrear(titulo="X" * 201, precio=100, direccion="Santiago"),
        "respeta el largo máximo del título")
rechaza(lambda: schemas.InteraccionCrear(tipo="Telegram"),
        "rechaza canales de interacción no soportados")
rechaza(lambda: schemas.TareaCrear(titulo="Llamar", estado="Archivada"),
        "rechaza estados de tarea desconocidos")
rechaza(lambda: schemas.TareaCrear(titulo="Llamar", fecha_limite="2026-02-30"),
        "rechaza fechas inexistentes")
rechaza(lambda: schemas.InteresCrear(propiedad_id=0),
        "rechaza identificadores de propiedad no positivos")
rechaza(lambda: schemas.InteresCrear(propiedad_id=1, nivel_interes="Mucho"),
        "rechaza niveles de interés desconocidos")


print("\n3. Duplicados por correo")

models.Base.metadata.create_all(bind=database.engine)
db = database.SessionLocal()
usuario = models.Usuario(
    nombre="Ejecutivo Prueba",
    email="ejecutivo@prueba.local",
    password_hash=seguridad.hashear_password("clave-de-prueba"),
    rol=seguridad.ROL_EJECUTIVO,
    activo=True,
)
db.add(usuario)
db.commit()
db.refresh(usuario)

primero = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Ana Soto", email="ana@correo.cl"),
    db=db,
    usuario=usuario,
)

try:
    main.crear_lead(
        lead=schemas.LeadCrear(nombre="Otra Ana", email="ANA@CORREO.CL"),
        db=db,
        usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 409, "crear un correo duplicado devuelve conflicto 409")
else:
    revisar(False, "crear un correo duplicado devuelve conflicto 409")

segundo = main.crear_lead(
    lead=schemas.LeadCrear(nombre="Luis Pérez", email="luis@correo.cl"),
    db=db,
    usuario=usuario,
)

try:
    main.actualizar_lead(
        lead_id=segundo.id,
        datos=schemas.LeadActualizar(email=primero.email.upper()),
        db=db,
        usuario=usuario,
    )
except HTTPException as error:
    revisar(error.status_code == 409, "editar hacia un correo duplicado devuelve conflicto 409")
else:
    revisar(False, "editar hacia un correo duplicado devuelve conflicto 409")

db.close()
database.engine.dispose()
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

print("\n" + "-" * 60)
if fallos:
    print(f"{len(fallos)} de {verificaciones} verificaciones fallaron")
    raise SystemExit(1)

print(f"Las {verificaciones} verificaciones pasaron")

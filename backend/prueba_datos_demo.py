"""Prueba que el escenario demo es coherente, ficticio e idempotente."""

import os

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prueba_datos_demo.db")
if os.path.exists(RUTA_BD):
    os.remove(RUTA_BD)

os.environ["DATABASE_URL"] = f"sqlite:///{RUTA_BD}"
os.environ["SECRET_KEY"] = "clave-temporal-solo-pruebas-32-bytes-minimo"

import cargar_datos_demo
import database
import models


models.Base.metadata.create_all(bind=database.engine)

primera = cargar_datos_demo.cargar()
segunda = cargar_datos_demo.cargar()

db = database.SessionLocal()
try:
    leads = db.query(models.Lead).filter(models.Lead.es_demo.is_(True)).all()
    propiedades = db.query(models.Propiedad).filter(models.Propiedad.titulo.like("[DEMO]%")).all()
    assert primera == (5, 5, 5), primera
    assert segunda == (0, 0, 0), segunda
    assert len(leads) == 5
    assert len(propiedades) == 5
    assert all(lead.email.endswith("@example.test") for lead in leads)
    assert all(lead.presupuesto_min <= lead.presupuesto_max for lead in leads)
    assert db.query(models.Interes).count() == 5
    assert db.query(models.Interaccion).count() == 5
    assert db.query(models.Tarea).count() == 4
    assert db.query(models.Oportunidad).count() == 5
finally:
    db.close()
    database.engine.dispose()
    if os.path.exists(RUTA_BD):
        os.remove(RUTA_BD)

print("Las 11 verificaciones de datos demo pasaron")

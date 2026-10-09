"""Regresión del catálogo MVP. Solo usa SQLite temporal y no llama al proveedor IA."""
import os
import asyncio
import json
import tempfile
import unittest
from types import SimpleNamespace

temporal = tempfile.TemporaryDirectory(prefix="crm_catalogo_")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(temporal.name, "catalogo.db")
os.environ["SECRET_KEY"] = "clave-temporal-de-pruebas-sin-uso-real"

import database
import main
import models
import seguridad


class ClientePruebas:
    """Ejecuta la API ASGI en memoria, sin servidor ni dependencias de pruebas extra."""

    def solicitar(self, metodo, ruta, datos=None):
        async def ejecutar():
            cuerpo = json.dumps(datos).encode() if datos is not None else b""
            enviado = False
            mensajes = []

            async def recibir():
                nonlocal enviado
                if not enviado:
                    enviado = True
                    return {"type": "http.request", "body": cuerpo, "more_body": False}
                await asyncio.Event().wait()

            async def enviar(mensaje):
                mensajes.append(mensaje)

            await main.app({
                "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                "method": metodo, "scheme": "http", "path": ruta, "raw_path": ruta.encode(),
                "query_string": b"", "root_path": "", "server": ("pruebas", 80),
                "client": ("127.0.0.1", 1), "headers": [(b"content-type", b"application/json")],
            }, recibir, enviar)
            inicio = next(m for m in mensajes if m["type"] == "http.response.start")
            contenido = b"".join(m.get("body", b"") for m in mensajes if m["type"] == "http.response.body")
            return SimpleNamespace(status_code=inicio["status"], text=contenido.decode(), json=lambda: json.loads(contenido))

        return asyncio.run(ejecutar())

    def get(self, ruta):
        return self.solicitar("GET", ruta)

    def post(self, ruta, json):
        return self.solicitar("POST", ruta, json)

    def put(self, ruta, json):
        return self.solicitar("PUT", ruta, json)


class CatalogoTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db = database.SessionLocal()
        self.admin = models.Usuario(nombre="Administrador prueba", email="admin@example.test", password_hash="sin-login", rol="admin")
        self.ejecutivo = models.Usuario(nombre="Ejecutivo prueba", email="ejecutivo@example.test", password_hash="sin-login", rol="ejecutivo")
        self.db.add_all([self.admin, self.ejecutivo])
        self.db.commit()
        self.usuario = self.admin
        main.app.dependency_overrides[database.obtener_db] = lambda: self.db
        main.app.dependency_overrides[seguridad.usuario_actual] = lambda: self.usuario
        self.client = ClientePruebas()
        self.base = {"titulo": "Propiedad ficticia", "precio": 100, "direccion": "Dirección ficticia"}

    def tearDown(self):
        main.app.dependency_overrides.clear()
        self.db.close()

    def crear(self, **campos):
        return self.client.post("/api/propiedades", json={**self.base, **campos})

    def test_ficha_completa_y_auditoria(self):
        r = self.crear(codigo_interno="PR-01", superficie_util=50.5, superficie_total=60,
                       dormitorios=2, banos=1, estacionamientos=0, bodega=False, gastos_comunes=0,
                       fecha_disponibilidad="2026-10-09", descripcion="Descripción ficticia",
                       caracteristicas="Terraza", fotografias=["https://example.test/uno.jpg", "https://example.test/dos.jpg"],
                       foto_principal="https://example.test/dos.jpg", propietario_nombre="Persona ficticia",
                       propietario_email="PERSONA@EXAMPLE.TEST", propietario_telefono="+56900000000", captador="Captador ficticio")
        self.assertEqual(r.status_code, 201, r.text)
        ficha = r.json()
        self.assertEqual(ficha["superficie_util"], 50.5)
        self.assertEqual(ficha["propietario_email"], "persona@example.test")
        self.assertEqual(self.client.get("/api/propiedades").json()[0], ficha)
        r = self.client.put(f"/api/propiedades/{ficha['id']}", json={"gastos_comunes": 100, "captador": "Otro captador"})
        self.assertEqual(r.status_code, 200, r.text)
        cambio = self.db.query(models.Auditoria).filter_by(accion="actualizar").one()
        self.assertIn("gastos_comunes: 0 -> 100", cambio.detalle)
        self.assertIn("captador:", cambio.detalle)

    def test_minima_y_campos_opcionales(self):
        self.usuario = self.ejecutivo
        r = self.crear()
        self.assertEqual(r.status_code, 201, r.text)
        ficha = r.json()
        self.assertEqual(ficha["fotografias"], [])
        self.assertIsNone(ficha["superficie_util"])
        r = self.client.put(f"/api/propiedades/{ficha['id']}", json={"descripcion": "Texto ficticio"})
        self.assertEqual(r.status_code, 200)
        r = self.client.put(f"/api/propiedades/{ficha['id']}", json={"descripcion": None})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json()["descripcion"])

    def test_rechaza_invalidos(self):
        casos = [{"superficie_util": -1}, {"superficie_total": -1}, {"estacionamientos": -1},
                 {"gastos_comunes": -1}, {"superficie_util": 60, "superficie_total": 50},
                 {"fecha_disponibilidad": "2026-02-30"}, {"fotografias": ["javascript:alert(1)"]},
                 {"fotografias": ["/foto.jpg"]}, {"fotografias": ["https://example.test/a.jpg"] * 2},
                 {"fotografias": [f"https://example.test/{i}.jpg" for i in range(21)]},
                 {"foto_principal": "https://example.test/fuera.jpg"}, {"propietario_email": "incorrecto"},
                 {"propietario_telefono": "abcdefgh"}, {"estado": "Desconocido"}]
        for campos in casos:
            with self.subTest(campos=campos):
                self.assertEqual(self.crear(**campos).status_code, 422)
        self.assertEqual(self.db.query(models.Propiedad).count(), 0)
        self.assertEqual(self.db.query(models.Auditoria).count(), 0)

    def test_actualizacion_parcial_coherente(self):
        ficha = self.crear(superficie_util=50, superficie_total=60,
                          fotografias=["https://example.test/a.jpg"], foto_principal="https://example.test/a.jpg").json()
        for cambio in [{"superficie_total": 40}, {"fotografias": []}, {"titulo": None}]:
            self.assertEqual(self.client.put(f"/api/propiedades/{ficha['id']}", json=cambio).status_code, 422)
        self.assertEqual(self.db.query(models.Auditoria).count(), 1)
        r = self.client.put(f"/api/propiedades/{ficha['id']}", json={"fotografias": [], "foto_principal": None})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["fotografias"], [])
        self.assertEqual(self.client.put("/api/propiedades/9999", json={"titulo": "Otro título"}).status_code, 404)

    def test_permisos_sin_alterar_datos(self):
        ficha = self.crear(propietario_nombre="Persona ficticia", propietario_email="persona@example.test", captador="Captador ficticio").json()
        self.usuario = self.ejecutivo
        lead = models.Lead(nombre="Lead ficticio", email="privacidad@example.test")
        self.db.add(lead)
        self.db.commit()
        sugerencias = self.client.get(f"/api/leads/{lead.id}/matching")
        self.assertEqual(sugerencias.status_code, 200)
        self.assertEqual(len(sugerencias.json()), 1)
        for campo in main.CAMPOS_PRIVADOS_PROPIEDAD:
            self.assertIsNone(sugerencias.json()[0]["propiedad"][campo])
        oculto = self.client.get("/api/propiedades").json()[0]
        for campo in main.CAMPOS_PRIVADOS_PROPIEDAD:
            self.assertIsNone(oculto[campo])
            self.assertEqual(self.client.put(f"/api/propiedades/{ficha['id']}", json={campo: None}).status_code, 403)
        self.assertEqual(self.crear(propietario_nombre="Otra persona").status_code, 403)
        r = self.client.put(f"/api/propiedades/{ficha['id']}", json={"estado": "Reservada"})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json()["propietario_nombre"])
        self.db.expire_all()
        self.assertEqual(self.db.get(models.Propiedad, ficha["id"]).propietario_nombre, "Persona ficticia")
        self.usuario = self.admin
        self.assertEqual(self.client.get("/api/propiedades").json()[0]["captador"], "Captador ficticio")

    def test_estados_y_matching(self):
        lead = models.Lead(nombre="Lead ficticio", email="lead@example.test")
        self.db.add(lead)
        self.db.commit()
        for estado in ["Disponible", "Reservada", "Vendida", "Arrendada", "Retirada"]:
            self.assertEqual(self.crear(estado=estado).status_code, 201)
        matches = self.client.get(f"/api/leads/{lead.id}/matching")
        self.assertEqual(matches.status_code, 200)
        self.assertEqual(len(matches.json()), 1)

    def test_limites_validos(self):
        fotos = [f"https://example.test/{i}.jpg" for i in range(20)]
        r = self.crear(superficie_util=0, superficie_total=0, estacionamientos=100,
                       gastos_comunes=999_999_999_999, fotografias=fotos, foto_principal=fotos[-1])
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["gastos_comunes"], 999_999_999_999)
        self.assertEqual(len(r.json()["fotografias"]), 20)
        for campo, valor in [("estacionamientos", 101), ("gastos_comunes", 1_000_000_000_000)]:
            self.assertEqual(self.crear(**{campo: valor}).status_code, 422)

    def test_exige_autenticacion(self):
        del main.app.dependency_overrides[seguridad.usuario_actual]
        self.assertEqual(self.client.get("/api/propiedades").status_code, 401)
        self.assertEqual(self.crear().status_code, 401)
        self.assertEqual(self.db.query(models.Propiedad).count(), 0)


if __name__ == "__main__":
    try:
        programa = unittest.main(exit=False)
    finally:
        database.engine.dispose()
        temporal.cleanup()
    raise SystemExit(0 if programa.result.wasSuccessful() else 1)

"""SCRUM-30 y SCRUM-31. API real, SQLite temporal y usuarios ficticios; sin llamadas de IA."""
import unittest
from unittest.mock import patch

# Reutiliza el cliente ASGI y su base temporal, nunca la conexión de Supabase.
from prueba_catalogo import ClientePruebas
import database
import main
import models
import seguridad


class AsignacionesTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db = database.SessionLocal()
        self.db.connection().exec_driver_sql('PRAGMA foreign_keys=ON')
        self.admin = models.Usuario(nombre='Admin ficticio', email='admin@example.test', password_hash='sin-login', rol='admin')
        self.uno = models.Usuario(nombre='Ejecutivo uno', email='uno@example.test', password_hash='sin-login', rol='ejecutivo')
        self.dos = models.Usuario(nombre='Ejecutivo dos', email='dos@example.test', password_hash='sin-login', rol='ejecutivo')
        self.inactivo = models.Usuario(nombre='Usuario inactivo', email='inactivo@example.test', password_hash='sin-login', activo=False)
        self.db.add_all([self.admin, self.uno, self.dos, self.inactivo]); self.db.commit()
        main.app.dependency_overrides[database.obtener_db] = lambda: self.db
        self.client = ClientePruebas()
        self.usuario = self.admin

    def tearDown(self):
        main.app.dependency_overrides.clear()
        self.db.close()

    def pedir(self, metodo, ruta, datos=None):
        cabeceras = [] if self.usuario is None else [(b'authorization', ('Bearer ' + seguridad.crear_token(self.usuario.id)).encode())]
        return self.client.solicitar(metodo, ruta, datos, cabeceras=cabeceras)

    def crear(self):
        r = self.pedir('POST', '/api/leads', {'nombre': 'Lead ficticio', 'email': 'lead@example.test', 'comunas_interes': 'Macul', 'presupuesto_max': 100})
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    def cambiar(self, lead, nuevo, anterior=None):
        return self.pedir('PUT', f'/api/leads/{lead["id"]}/asignacion', {
            'ejecutivo_id': nuevo, 'ejecutivo_anterior_id': lead['ejecutivo_id'] if anterior is None else anterior,
        })

    def test_creacion_registra_responsable_e_historial(self):
        self.usuario = self.uno; lead = self.crear()
        self.assertEqual(lead['ejecutivo_id'], self.uno.id)
        self.assertEqual(lead['ejecutivo_nombre'], 'Ejecutivo uno')
        r = self.pedir('GET', f'/api/leads/{lead["id"]}/asignaciones')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['total'], 1)
        item = r.json()['items'][0]
        self.assertIsNone(item['anterior_id'])
        self.assertEqual(item['nuevo_id'], self.uno.id)
        self.assertEqual(item['autor_nombre'], 'Ejecutivo uno')
        self.assertTrue(item['fecha_creacion'])

    def test_reasigna_persiste_y_audita_sin_alterar_perfil(self):
        lead = self.crear()
        r = self.cambiar(lead, self.dos.id)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['ejecutivo_nombre'], 'Ejecutivo dos')
        self.db.expire_all()
        consultado = self.pedir('GET', '/api/leads').json()[0]
        self.assertEqual(consultado['ejecutivo_id'], self.dos.id)
        for campo in ['nombre', 'email', 'presupuesto_max', 'comunas_interes', 'estado']:
            self.assertEqual(lead[campo], consultado[campo])
        historial = self.pedir('GET', f'/api/leads/{lead["id"]}/asignaciones').json()
        self.assertEqual(historial['total'], 2)
        self.assertEqual(historial['items'][0]['anterior_nombre'], 'Admin ficticio')
        self.assertEqual(historial['items'][0]['nuevo_nombre'], 'Ejecutivo dos')
        registro = self.db.query(models.Auditoria).order_by(models.Auditoria.id.desc()).first()
        self.assertEqual(registro.usuario_id, self.admin.id)
        self.assertIn('Admin ficticio -> Ejecutivo dos', registro.detalle)

    def test_guardar_sin_cambio_no_inventa_movimientos(self):
        lead = self.crear()
        auditorias = self.db.query(models.Auditoria).count()
        self.assertEqual(self.cambiar(lead, self.admin.id).status_code, 200)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 1)
        self.assertEqual(self.db.query(models.Auditoria).count(), auditorias)

    def test_ejecutivo_puede_consultar_no_reasignar_ni_listar_cuentas(self):
        lead = self.crear(); self.usuario = self.uno
        self.assertEqual(self.cambiar(lead, self.dos.id).status_code, 403)
        self.assertEqual(self.pedir('GET', '/api/ejecutivos').status_code, 403)
        self.assertEqual(self.pedir('GET', f'/api/leads/{lead["id"]}/asignaciones').status_code, 200)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 1)

    def test_requiere_sesion_y_cuenta_activa(self):
        lead = self.crear()
        for usuario in [None, self.inactivo]:
            self.usuario = usuario
            self.assertEqual(self.cambiar(lead, self.dos.id).status_code, 401)
            self.assertEqual(self.pedir('GET', f'/api/leads/{lead["id"]}/asignaciones').status_code, 401)

    def test_catalogo_solo_usuarios_activos_y_datos_minimos(self):
        r = self.pedir('GET', '/api/ejecutivos')
        self.assertEqual(r.status_code, 200)
        self.assertEqual({u['id'] for u in r.json()}, {self.admin.id, self.uno.id, self.dos.id})
        self.assertTrue(all(set(u) == {'id', 'nombre', 'rol'} for u in r.json()))

    def test_rechaza_inexistentes_inactivos_y_entradas_invalidas(self):
        lead = self.crear()
        for destino in [99999, self.inactivo.id, 0, -1, None, True, '2']:
            with self.subTest(destino=destino):
                self.assertEqual(self.cambiar(lead, destino).status_code, 422)
        for datos in [{}, {'ejecutivo_id': self.dos.id}, {'ejecutivo_id': self.dos.id, 'ejecutivo_anterior_id': self.admin.id, 'rol': 'admin'}]:
            self.assertEqual(self.pedir('PUT', f'/api/leads/{lead["id"]}/asignacion', datos).status_code, 422)
        self.assertEqual(self.pedir('GET', '/api/leads/99999/asignaciones').status_code, 404)
        self.assertEqual(self.pedir('PUT', '/api/leads/99999/asignacion', {'ejecutivo_id': self.dos.id, 'ejecutivo_anterior_id': None}).status_code, 404)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 1)

    def test_conflicto_no_sobrescribe_un_cambio_mas_reciente(self):
        lead = self.crear()
        self.assertEqual(self.cambiar(lead, self.uno.id).status_code, 200)
        self.assertEqual(self.cambiar(lead, self.dos.id).status_code, 409)
        self.assertEqual(self.db.get(models.Lead, lead['id']).ejecutivo_id, self.uno.id)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 2)

    def test_lead_antiguo_sin_historia_no_recibe_fechas_inventadas(self):
        antiguo = models.Lead(nombre='Lead anterior', email='anterior@example.test')
        self.db.add(antiguo); self.db.commit()
        self.assertEqual(self.pedir('GET', f'/api/leads/{antiguo.id}/asignaciones').json()['total'], 0)
        r = self.pedir('PUT', f'/api/leads/{antiguo.id}/asignacion', {'ejecutivo_id': self.uno.id, 'ejecutivo_anterior_id': None})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 1)

    def test_paginacion_y_conservacion_de_nombres_historicos(self):
        lead = self.crear()
        for _ in range(4):
            destino = self.uno.id if lead['ejecutivo_id'] != self.uno.id else self.dos.id
            lead = self.cambiar(lead, destino).json()
        primero = main.listar_asignaciones(lead['id'], pagina=1, por_pagina=2, db=self.db)
        segundo = main.listar_asignaciones(lead['id'], pagina=2, por_pagina=2, db=self.db)
        self.assertEqual(primero['total'], 5)
        self.assertFalse({x.id for x in primero['items']} & {x.id for x in segundo['items']})
        respuesta = self.pedir('GET', f'/api/leads/{lead["id"]}/asignaciones?pagina=2&por_pagina=2')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['pagina'], 2)
        self.assertEqual([x['id'] for x in respuesta.json()['items']], [x.id for x in segundo['items']])
        for consulta in ['pagina=0', 'por_pagina=0', 'por_pagina=101']:
            self.assertEqual(self.pedir('GET', f'/api/leads/{lead["id"]}/asignaciones?{consulta}').status_code, 422)
        self.uno.nombre = 'Nombre modificado'; self.db.commit()
        self.assertTrue(any(x.nuevo_nombre == 'Ejecutivo uno' for x in self.db.query(models.AsignacionLead).all()))

    def test_fallo_de_auditoria_revierte_responsable_e_historial(self):
        lead = self.crear()
        with patch.object(main.auditoria, 'registrar', side_effect=RuntimeError('Fallo simulado')):
            with self.assertRaises(RuntimeError): self.cambiar(lead, self.dos.id)
        self.db.rollback()
        self.assertEqual(self.db.get(models.Lead, lead['id']).ejecutivo_id, self.admin.id)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 1)

    def test_borrar_cuentas_o_lead_conserva_el_movimiento(self):
        lead = self.crear()
        self.cambiar(lead, self.dos.id)
        self.db.delete(self.dos); self.db.commit()
        ultimo = self.db.query(models.AsignacionLead).order_by(models.AsignacionLead.id.desc()).first()
        self.db.refresh(ultimo)
        self.assertIsNone(ultimo.nuevo_id)
        self.assertEqual(ultimo.nuevo_nombre, 'Ejecutivo dos')
        self.db.delete(self.db.get(models.Lead, lead['id'])); self.db.commit(); self.db.refresh(ultimo)
        self.assertIsNone(ultimo.lead_id)
        self.assertEqual(ultimo.lead_nombre, 'Lead ficticio')


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Carteras con SQLite temporal y cuentas ficticias; no consulta Supabase ni IA."""
import unittest

from prueba_catalogo import ClientePruebas
import database
import main
import models
import seguridad


class CarteraTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db = database.SessionLocal()
        self.admin = models.Usuario(nombre='Admin ficticio', email='admin@example.test', password_hash='sin-login', rol='admin')
        self.uno = models.Usuario(nombre='Ejecutivo uno', email='uno@example.test', password_hash='sin-login', rol='ejecutivo')
        self.dos = models.Usuario(nombre='Ejecutivo dos', email='dos@example.test', password_hash='sin-login', rol='ejecutivo')
        self.vacio = models.Usuario(nombre='Ejecutivo sin cartera', email='vacio@example.test', password_hash='sin-login', rol='ejecutivo')
        self.inactivo = models.Usuario(nombre='Inactivo ficticio', email='inactivo@example.test', password_hash='sin-login', activo=False)
        self.db.add_all([self.admin, self.uno, self.dos, self.vacio, self.inactivo]); self.db.flush()
        self.leads = [
            models.Lead(nombre='Cliente norte', email='norte@example.test', ejecutivo_id=self.uno.id, prioridad='Alta'),
            models.Lead(nombre='Cliente oriente', email='oriente@example.test', ejecutivo_id=self.uno.id, estado='Cerrado'),
            models.Lead(nombre='Cliente sur', email='sur@example.test', ejecutivo_id=self.dos.id),
            models.Lead(nombre='Cliente sin asignar', email='sin@example.test'),
            models.Lead(nombre='Cliente administración', email='gestion@example.test', ejecutivo_id=self.admin.id),
        ]
        self.db.add_all(self.leads); self.db.commit()
        self.client = ClientePruebas()
        self.usuario = self.admin
        main.app.dependency_overrides[database.obtener_db] = lambda: self.db

    def tearDown(self):
        main.app.dependency_overrides.clear()
        self.db.close()

    def pedir(self, consulta='', metodo='GET', ruta=None, datos=None):
        headers = [(b'authorization', ('Bearer ' + seguridad.crear_token(self.usuario.id)).encode())] if self.usuario else []
        return self.client.solicitar(metodo, ruta or '/api/leads' + consulta, datos, cabeceras=headers)

    def ids(self, consulta=''):
        respuesta = self.pedir(consulta)
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        return {r['id'] for r in respuesta.json()}

    def test_todos_conserva_visibilidad_existente_para_cada_rol(self):
        esperados = {lead.id for lead in self.leads}
        for usuario in [self.admin, self.uno, self.dos, self.vacio]:
            self.usuario = usuario
            self.assertEqual(self.ids(), esperados)
            self.assertEqual(self.ids('?cartera=todos'), esperados)

    def test_mi_cartera_se_resuelve_con_la_identidad_de_la_sesion(self):
        for usuario, indices in [(self.uno, [0, 1]), (self.dos, [2]), (self.admin, [4]), (self.vacio, [])]:
            self.usuario = usuario
            self.assertEqual(self.ids('?cartera=mia'), {self.leads[i].id for i in indices})

    def test_admin_filtra_por_responsables_activos_o_sin_asignar(self):
        self.assertEqual(self.ids(f'?ejecutivo_id={self.uno.id}'), {self.leads[0].id, self.leads[1].id})
        self.assertEqual(self.ids(f'?ejecutivo_id={self.admin.id}'), {self.leads[4].id})
        self.assertEqual(self.ids(f'?ejecutivo_id={self.vacio.id}'), set())
        self.assertEqual(self.ids('?sin_asignar=true'), {self.leads[3].id})
        self.assertEqual(self.ids('?sin_asignar=false'), {lead.id for lead in self.leads})

    def test_ejecutivo_no_usa_filtros_administrativos_por_api(self):
        self.usuario = self.uno
        for consulta in [f'?ejecutivo_id={self.dos.id}', f'?ejecutivo_id={self.uno.id}', '?sin_asignar=true']:
            self.assertEqual(self.pedir(consulta).status_code, 403)
        self.assertEqual(self.ids('?cartera=mia'), {self.leads[0].id, self.leads[1].id})

    def test_filtros_incompatibles_no_se_interpretan_arbitrariamente(self):
        for consulta in [f'?cartera=mia&ejecutivo_id={self.uno.id}', '?cartera=mia&sin_asignar=true',
                f'?ejecutivo_id={self.uno.id}&sin_asignar=true']:
            self.assertEqual(self.pedir(consulta).status_code, 400)

    def test_valores_invalidos_e_inactivos_se_rechazan(self):
        for consulta in ['?cartera=otra', '?ejecutivo_id=0', '?ejecutivo_id=-1', '?ejecutivo_id=abc', '?sin_asignar=talvez']:
            self.assertEqual(self.pedir(consulta).status_code, 422)
        self.assertEqual(self.pedir('?ejecutivo_id=999999').status_code, 404)
        self.assertEqual(self.pedir(f'?ejecutivo_id={self.inactivo.id}').status_code, 422)

    def test_sin_sesion_y_cuenta_inactiva_no_consultan_carteras(self):
        for usuario in [None, self.inactivo]:
            self.usuario = usuario
            for consulta in ['', '?cartera=mia', '?sin_asignar=true']:
                self.assertEqual(self.pedir(consulta).status_code, 401)

    def test_prioridad_nombre_y_orden_se_conservan_al_filtrar(self):
        todos = self.pedir().json()
        filtrados = self.pedir(f'?ejecutivo_id={self.uno.id}').json()
        self.assertEqual(filtrados, [r for r in todos if r['ejecutivo_id'] == self.uno.id])
        self.assertTrue(all(r['ejecutivo_nombre'] == self.uno.nombre for r in filtrados))
        self.assertTrue(all('puntaje' in r and 'categoria' in r for r in filtrados))

    def test_leer_no_modifica_clientes_historial_ni_auditoria(self):
        anterior = [{c.name: getattr(lead, c.name) for c in models.Lead.__table__.columns} for lead in self.leads]
        for consulta in ['', '?cartera=mia', '?sin_asignar=true', f'?ejecutivo_id={self.uno.id}']:
            self.ids(consulta)
        self.db.expire_all()
        posterior = [{c.name: getattr(lead, c.name) for c in models.Lead.__table__.columns} for lead in self.leads]
        self.assertEqual(anterior, posterior)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 0)
        self.assertEqual(self.db.query(models.Auditoria).count(), 0)

    def test_reasignacion_se_refleja_en_ambas_carteras_tras_consultar(self):
        self.usuario = self.uno
        self.assertIn(self.leads[0].id, self.ids('?cartera=mia'))
        self.usuario = self.admin
        cambio = self.pedir(metodo='PUT', ruta=f'/api/leads/{self.leads[0].id}/asignacion',
            datos={'ejecutivo_id': self.dos.id, 'ejecutivo_anterior_id': self.uno.id})
        self.assertEqual(cambio.status_code, 200, cambio.text)
        self.usuario = self.uno
        self.assertNotIn(self.leads[0].id, self.ids('?cartera=mia'))
        self.usuario = self.dos
        self.assertEqual(self.ids('?cartera=mia'), {self.leads[0].id, self.leads[2].id})
        self.assertEqual(len(self.ids()), 5)
        self.assertEqual(self.db.query(models.AsignacionLead).count(), 1)
        self.assertEqual(self.db.query(models.Auditoria).count(), 1)


if __name__ == '__main__':
    unittest.main()

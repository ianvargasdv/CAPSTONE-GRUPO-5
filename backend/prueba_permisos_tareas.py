"""Permisos de tareas por cartera. SQLite temporal; sin llamadas externas."""
import json
import unittest
from unittest.mock import patch

from prueba_catalogo import ClientePruebas
import database
import main
import models
import seguridad


class PermisosTareasTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db = database.SessionLocal()
        self.uno = models.Usuario(nombre='Ejecutivo uno', email='uno@example.test', rol='ejecutivo', password_hash='sin-login')
        self.dos = models.Usuario(nombre='Ejecutivo dos', email='dos@example.test', rol='ejecutivo', password_hash='sin-login')
        self.admin = models.Usuario(nombre='Admin', email='admin@example.test', rol='admin', password_hash='sin-login')
        self.db.add_all([self.uno, self.dos, self.admin]); self.db.flush()
        self.propio = models.Lead(nombre='Cliente propio', email='propio@example.test', ejecutivo_id=self.uno.id)
        self.ajeno = models.Lead(nombre='Cliente ajeno', email='ajeno@example.test', ejecutivo_id=self.dos.id)
        self.libre = models.Lead(nombre='Cliente sin asignar', email='libre@example.test')
        self.db.add_all([self.propio, self.ajeno, self.libre]); self.db.flush()
        self.tarea = models.Tarea(titulo='Propia', lead_id=self.propio.id)
        self.otra = models.Tarea(titulo='Ajena', lead_id=self.ajeno.id)
        self.sin_lead = models.Tarea(titulo='Sin lead')
        self.sin_asignar = models.Tarea(titulo='Sin responsable', lead_id=self.libre.id)
        self.db.add_all([self.tarea, self.otra, self.sin_lead, self.sin_asignar]); self.db.commit()
        main.app.dependency_overrides[database.obtener_db] = lambda: self.db
        self.addCleanup(main.app.dependency_overrides.clear)
        self.addCleanup(self.db.close)
        self.client = ClientePruebas()

    def pedir(self, metodo, ruta='/api/tareas', datos=None, usuario=None):
        u = usuario or self.uno
        return self.client.solicitar(metodo, ruta, datos,
            cabeceras=[(b'authorization', ('Bearer '+seguridad.crear_token(u.id)).encode())])

    def test_listado_ejecutivo_solo_sus_tareas_admin_todas(self):
        r = self.pedir('GET')
        self.assertEqual(r.status_code, 200)
        self.assertEqual([t['id'] for t in r.json()], [self.tarea.id])
        self.assertEqual(len(self.pedir('GET', usuario=self.admin).json()), 4)
        self.assertEqual(self.client.solicitar('GET', '/api/tareas').status_code, 401)

    def test_ejecutivo_crea_en_su_lead_y_rechaza_ajenos_y_sin_lead(self):
        r = self.pedir('POST', datos={'titulo': 'Otra acción', 'lead_id': self.propio.id})
        self.assertEqual(r.status_code, 201, r.text)
        inicial = self.db.query(models.Tarea).count()
        auditorias = self.db.query(models.Auditoria).count()
        for lead_id in [self.ajeno.id, self.libre.id, None, 999999]:
            with self.subTest(lead_id=lead_id):
                r = self.pedir('POST', datos={'titulo': 'No debe crearse', 'lead_id': lead_id})
                self.assertIn(r.status_code, [403, 404], r.text)
        self.assertEqual(self.db.query(models.Tarea).count(), inicial)
        self.assertEqual(self.db.query(models.Auditoria).count(), auditorias)

    def test_admin_crea_para_otro_ejecutivo_o_sin_lead(self):
        for lead_id in [self.ajeno.id, None]:
            r = self.pedir('POST', datos={'titulo': 'Acción de administración', 'lead_id': lead_id}, usuario=self.admin)
            self.assertEqual(r.status_code, 201, r.text)
        r = self.pedir('POST', datos={'titulo': 'Inválida', 'lead_id': 999999}, usuario=self.admin)
        self.assertEqual(r.status_code, 404)

    def test_editar_completar_y_eliminar_propias(self):
        ruta = f'/api/tareas/{self.tarea.id}'
        for datos in [{'descripcion': 'Revisada'}, {'estado': 'Completada'}]:
            r = self.pedir('PUT', ruta, datos)
            self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(self.pedir('DELETE', ruta).status_code, 204)
        self.assertIsNone(self.db.get(models.Tarea, self.tarea.id))

    def test_no_edita_completa_elimina_ajenas_ni_huerfanas_por_id(self):
        for tarea in [self.otra, self.sin_lead, self.sin_asignar]:
            ruta = f'/api/tareas/{tarea.id}'
            for metodo, datos in [('PUT', {'titulo': 'Manipulada'}), ('PUT', {'estado': 'Completada'}), ('DELETE', None)]:
                with self.subTest(tarea=tarea.id, metodo=metodo, datos=datos):
                    self.assertEqual(self.pedir(metodo, ruta, datos).status_code, 404)
        self.assertEqual(self.db.query(models.Tarea).count(), 4)
        self.assertEqual(self.db.query(models.Auditoria).count(), 0)

    def test_no_transfiere_una_tarea_propia_a_cliente_ajeno_o_sin_lead(self):
        for lead_id in [self.ajeno.id, self.libre.id, None, 999999]:
            r = self.pedir('PUT', f'/api/tareas/{self.tarea.id}', {'lead_id': lead_id, 'titulo': 'Manipulada'})
            self.assertIn(r.status_code, [403, 404], r.text)
        self.db.refresh(self.tarea)
        self.assertEqual(self.tarea.titulo, 'Propia')
        self.assertEqual(self.tarea.lead_id, self.propio.id)

    def test_admin_puede_gestionar_tareas_sin_lead_y_ajenas(self):
        for tarea in [self.otra, self.sin_lead, self.sin_asignar]:
            ruta = f'/api/tareas/{tarea.id}'
            r = self.pedir('PUT', ruta, {'estado': 'Completada'}, usuario=self.admin)
            self.assertEqual(r.status_code, 200, r.text)
            self.assertEqual(self.pedir('DELETE', ruta, usuario=self.admin).status_code, 204)

    def test_reasignar_lead_cambia_acceso_con_la_misma_sesion(self):
        token = seguridad.crear_token(self.uno.id)
        headers = [(b'authorization', ('Bearer '+token).encode())]
        self.propio.ejecutivo_id = self.dos.id
        self.db.commit()
        r = self.client.solicitar('GET', '/api/tareas', cabeceras=headers)
        self.assertEqual(r.json(), [])
        r = self.client.solicitar('PUT', f'/api/tareas/{self.tarea.id}', {'estado': 'Completada'}, cabeceras=headers)
        self.assertEqual(r.status_code, 404)
        self.assertEqual({t['id'] for t in self.pedir('GET', usuario=self.dos).json()}, {self.tarea.id, self.otra.id})

    def preparar_chat(self, cliente, usuario=None):
        resultado = {'texto': json.dumps({'accion': 'crear_tarea', 'cliente': cliente,
            'titulo': 'Acción desde chat', 'descripcion': None, 'aclaracion': None}),
            'modelo': 'simulado', 'tokens_entrada': 1, 'tokens_salida': 1, 'costo_estimado_usd': 0}
        with patch('ia.generar_analisis', return_value=resultado):
            return self.pedir('POST', '/api/asistente/tareas/preparar', {'mensaje': f'Crea para {cliente} una tarea'}, usuario=usuario)

    def test_chat_no_ofrece_clientes_ajenos_ni_permite_confirmarlos(self):
        r = self.preparar_chat(self.ajeno.nombre)
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()['clientes'], [])
        p = r.json()['id']
        r = self.pedir('POST', f'/api/asistente/tareas/{p}/confirmar', {'lead_id': self.ajeno.id, 'titulo': 'No crear'})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.db.query(models.Tarea).count(), 4)

    def test_chat_revalida_responsable_antes_de_confirmar_y_en_reintentos(self):
        p = self.preparar_chat(self.propio.nombre).json()['id']
        datos = {'lead_id': self.propio.id, 'titulo': 'Acción desde chat'}
        r = self.pedir('POST', f'/api/asistente/tareas/{p}/confirmar', datos)
        self.assertEqual(r.status_code, 200, r.text)
        self.propio.ejecutivo_id = self.dos.id
        self.db.commit()
        self.assertEqual(self.pedir('POST', f'/api/asistente/tareas/{p}/confirmar', datos).status_code, 404)
        self.assertEqual(self.db.query(models.Tarea).count(), 5)
        # Otra propuesta que pierde acceso antes de la primera confirmación.
        self.propio.ejecutivo_id = self.uno.id
        self.db.commit()
        p = self.preparar_chat(self.propio.nombre).json()['id']
        self.propio.ejecutivo_id = self.dos.id
        self.db.commit()
        self.assertEqual(self.pedir('POST', f'/api/asistente/tareas/{p}/confirmar', datos).status_code, 409)


if __name__ == '__main__':
    unittest.main()

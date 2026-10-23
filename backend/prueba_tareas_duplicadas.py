"""Regresión de tareas repetidas, con API real en memoria y SQLite temporal."""
import unittest
from prueba_catalogo import ClientePruebas
import database
import main
import models
import seguridad


class TareasDuplicadasTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db = database.SessionLocal()
        self.usuario = models.Usuario(nombre='Usuario ficticio', email='usuario@example.test', password_hash='sin-login', rol='ejecutivo')
        self.lead = models.Lead(nombre='Cliente ficticio A', email='a@example.test')
        self.otro = models.Lead(nombre='Cliente ficticio B', email='b@example.test')
        self.db.add_all([self.usuario, self.lead, self.otro]);self.db.commit()
        self.cabeceras = [(b'authorization', ('Bearer ' + seguridad.crear_token(self.usuario.id)).encode())]
        main.app.dependency_overrides[database.obtener_db] = lambda: self.db
        self.client = ClientePruebas()
        self.datos = {'titulo':'Confirmar búsqueda', 'descripcion':'Confirmar terreno y estacionamientos.', 'lead_id':self.lead.id}

    def tearDown(self):
        main.app.dependency_overrides.clear()
        self.db.close()

    def crear(self, **cambios):
        return self.client.solicitar('POST','/api/tareas',{**self.datos, **cambios},self.cabeceras)

    def test_rechaza_repetida_sin_tarea_ni_auditoria_adicional(self):
        self.assertEqual(self.crear().status_code,201)
        auditorias = self.db.query(models.Auditoria).count()
        self.assertEqual(self.crear().status_code,409)
        self.assertEqual(self.db.query(models.Tarea).count(),1)
        self.assertEqual(self.db.query(models.Auditoria).count(),auditorias)

    def test_normaliza_espacios_mayusculas_y_tildes(self):
        self.assertEqual(self.crear().status_code,201)
        self.assertEqual(self.crear(titulo='  CONFIRMAR   BUSQUEDA  ',descripcion=' confirmar terreno y estacionamientos. ').status_code,409)

    def test_no_confunde_distinto_cliente_ni_detalles_distintos(self):
        self.assertEqual(self.crear().status_code,201)
        self.assertEqual(self.crear(lead_id=self.otro.id).status_code,201)
        self.assertEqual(self.crear(descripcion='Enviar los antecedentes solicitados.').status_code,201)

    def test_tarea_completada_permite_nuevo_seguimiento(self):
        primera = self.crear().json()
        resultado = self.client.solicitar('PUT',f"/api/tareas/{primera['id']}",{'estado':'Completada'},self.cabeceras)
        self.assertEqual(resultado.status_code,200)
        self.assertEqual(self.crear().status_code,201)

    def test_sin_cliente_no_impone_una_unicidad_global(self):
        self.assertEqual(self.crear(lead_id=None).status_code,201)
        self.assertEqual(self.crear(lead_id=None).status_code,201)

    def test_actualizar_misma_tarea_conserva_su_identidad(self):
        primera = self.crear().json()
        resultado = self.client.solicitar('PUT',f"/api/tareas/{primera['id']}",{'titulo':self.datos['titulo'],'estado':'En Progreso'},self.cabeceras)
        self.assertEqual(resultado.status_code,200,resultado.text)
        self.assertEqual(resultado.json()['id'],primera['id'])
        self.assertEqual(self.db.query(models.Tarea).count(),1)

    def test_editar_otra_tarea_no_permite_copiar_la_pendiente(self):
        self.crear()
        segunda = self.crear(titulo='Otra acción',descripcion='Detalle distinto.').json()
        resultado = self.client.solicitar('PUT',f"/api/tareas/{segunda['id']}",{'titulo':self.datos['titulo'],'descripcion':self.datos['descripcion']},self.cabeceras)
        self.assertEqual(resultado.status_code,409)
        self.assertEqual(self.db.query(models.Tarea).filter_by(id=segunda['id']).one().titulo,'Otra acción')

    def test_reasignar_no_permite_crear_una_repetida_en_otro_cliente(self):
        self.crear()
        segunda = self.crear(lead_id=self.otro.id).json()
        resultado = self.client.solicitar('PUT',f"/api/tareas/{segunda['id']}",{'lead_id':self.lead.id},self.cabeceras)
        self.assertEqual(resultado.status_code,409)
        self.assertEqual(self.db.query(models.Tarea).filter_by(id=segunda['id']).one().lead_id,self.otro.id)


if __name__ == '__main__':
    unittest.main(verbosity=2)

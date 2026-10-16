"""Carga y protección del escenario en SQLite temporal, nunca Supabase."""
import unittest
from prueba_catalogo import ClientePruebas
import database
import models
import schemas
import cargar_escenario_pruebas as escenario


class EscenarioTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db = database.SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_carga_completa_valida_y_marcada_como_ficticia(self):
        resultado=escenario.cargar()
        self.assertEqual(resultado,dict(leads=24,propiedades=18,intereses=24,interacciones=18,tareas=22,oportunidades=18,visitas=6))
        for lead in self.db.query(models.Lead).all():
            self.assertTrue(lead.es_demo)
            self.assertNotIn('Demo',lead.nombre)
            self.assertTrue(lead.email.endswith('@example.test'))
            self.assertIsNone(lead.telefono)
            schemas.LeadCrear.model_validate({c.name:getattr(lead,c.name) for c in models.Lead.__table__.columns})
        for propiedad in self.db.query(models.Propiedad).all():
            self.assertNotIn('DEMO',propiedad.titulo)
            self.assertTrue(propiedad.descripcion.startswith(escenario.MARCA))
            self.assertIsNone(propiedad.propietario_telefono)
            schemas.PropiedadCrear.model_validate({c.name:getattr(propiedad,c.name) for c in models.Propiedad.__table__.columns})
        self.assertEqual(self.db.query(models.Auditoria).count(),sum(resultado.values()))

    def test_segunda_carga_no_duplica_ni_sobrescribe_ediciones(self):
        escenario.cargar()
        lead=self.db.query(models.Lead).first(); lead.nombre='Nombre editado por el usuario'
        propiedad=self.db.query(models.Propiedad).first(); propiedad.precio=999999
        tarea=self.db.query(models.Tarea).first(); tarea.estado='Completada'
        self.db.commit()
        auditorias=self.db.query(models.Auditoria).count()
        self.assertTrue(all(cantidad==0 for cantidad in escenario.cargar().values()))
        self.db.expire_all()
        self.assertEqual(lead.nombre,'Nombre editado por el usuario')
        self.assertEqual(propiedad.precio,999999)
        self.assertEqual(tarea.estado,'Completada')
        self.assertEqual(self.db.query(models.Auditoria).count(),auditorias)

    def test_colision_con_un_lead_no_ficticio_revierte_toda_la_carga(self):
        self.db.add(models.Lead(nombre='Registro existente',email='cliente.escenario.001@example.test',es_demo=False))
        self.db.commit()
        with self.assertRaises(ValueError): escenario.cargar()
        self.assertEqual(self.db.query(models.Propiedad).count(),0)
        self.assertEqual(self.db.query(models.Lead).count(),1)
        self.assertEqual(self.db.query(models.Auditoria).count(),0)

    def test_no_adopta_una_propiedad_ajena_con_el_mismo_codigo(self):
        self.db.add(models.Propiedad(titulo='Inmueble existente',precio=100,direccion='Sin precisar',codigo_interno='PRUEBA-CRM-001'))
        self.db.commit()
        with self.assertRaises(ValueError): escenario.cargar()
        self.assertEqual(self.db.query(models.Propiedad).count(),1)
        self.assertEqual(self.db.query(models.Lead).count(),0)

    def test_preserva_los_registros_no_relacionados(self):
        self.db.add(models.Lead(nombre='Registro previo',email='previo@example.test',es_demo=False))
        self.db.commit()
        escenario.cargar()
        self.assertEqual(self.db.query(models.Lead).count(),25)
        self.assertEqual(self.db.query(models.Lead).filter_by(es_demo=False).one().nombre,'Registro previo')


if __name__=='__main__': unittest.main(verbosity=2)

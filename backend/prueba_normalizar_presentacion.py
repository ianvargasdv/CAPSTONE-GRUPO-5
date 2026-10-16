"""Normalización en SQLite: conserva origen ficticio y textos históricos."""
import unittest
from prueba_catalogo import ClientePruebas
import database
import models
import normalizar_presentacion as normalizar
import cargar_datos_demo
import schemas


class NormalizacionTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db=database.SessionLocal()
        self.lead=models.Lead(nombre='Cliente ficticio (Demo)',email='cliente@example.test',es_demo=True,origen='Demo capstone')
        self.propiedad=models.Propiedad(titulo='[DEMO] Casa con patio',precio=7000,direccion='Sector ficticio',moneda='UF')
        self.db.add_all([self.lead,self.propiedad]); self.db.flush()
        self.db.add(models.Interes(lead_id=self.lead.id,propiedad_id=self.propiedad.id))
        self.db.add(models.Auditoria(accion='crear',entidad='lead',descripcion='Registro histórico: Cliente ficticio (Demo)'))
        self.db.commit()

    def tearDown(self): self.db.close()

    def test_vista_previa_no_modifica(self):
        self.assertEqual(normalizar.normalizar(),dict(leads=1,propiedades=1))
        self.db.expire_all()
        self.assertTrue(self.lead.nombre.endswith('(Demo)'))
        self.assertEqual(self.db.query(models.Auditoria).count(),1)

    def test_aplicar_conserva_relaciones_ficha_y_origen(self):
        normalizar.normalizar(True); self.db.expire_all()
        self.assertEqual(self.lead.nombre,'Cliente ficticio')
        self.assertTrue(self.lead.es_demo)
        self.assertEqual(self.lead.origen,'Escenario de prueba')
        self.assertEqual(self.propiedad.titulo,'Casa con patio')
        self.assertEqual(self.propiedad.precio,7000)
        self.assertEqual(self.propiedad.moneda,'UF')
        self.assertTrue(self.propiedad.descripcion.startswith(normalizar.MARCA_LEGADO))
        self.assertEqual(self.db.query(models.Interes).one().propiedad_id,self.propiedad.id)
        self.assertEqual(self.db.query(models.Auditoria).order_by(models.Auditoria.id).first().descripcion,
            'Registro histórico: Cliente ficticio (Demo)')

    def test_segunda_ejecucion_no_repite_cambios_ni_auditoria(self):
        normalizar.normalizar(True)
        self.assertEqual(normalizar.normalizar(True),dict(leads=0,propiedades=0))
        self.assertEqual(self.db.query(models.Auditoria).count(),3)

    def test_no_renombra_un_cliente_no_marcado_como_prueba(self):
        self.lead.es_demo=False; self.db.commit()
        normalizar.normalizar(True); self.db.expire_all()
        self.assertTrue(self.lead.nombre.endswith('(Demo)'))

    def test_limpieza_limitada_a_los_marcadores_no_a_palabras_internas(self):
        self.assertEqual(normalizar.nombre_natural('  Persona (dEmO)  '),'Persona')
        self.assertEqual(normalizar.titulo_natural('[demo] Departamento'),'Departamento')
        self.assertEqual(normalizar.nombre_natural('Demóstenes Pérez'),'Demóstenes Pérez')
        self.assertEqual(normalizar.titulo_natural('Casa con sala demo'),'Casa con sala demo')
        self.assertEqual(normalizar.nombre_natural('(Demo)'),'(Demo)')

    def test_cargador_inicial_no_duplica_propiedades_normalizadas(self):
        cargar_datos_demo.cargar()
        normalizar.normalizar(True)
        cantidad=self.db.query(models.Propiedad).count()
        self.assertEqual(cargar_datos_demo.cargar(),(0,0,0,0))
        self.assertEqual(self.db.query(models.Propiedad).count(),cantidad)

    def test_titulo_de_propiedad_respeta_el_limite_real_de_la_columna(self):
        schemas.PropiedadCrear(titulo='x'*150,precio=100,direccion='Sector ficticio')
        with self.assertRaises(ValueError):
            schemas.PropiedadCrear(titulo='x'*151,precio=100,direccion='Sector ficticio')


if __name__=='__main__': unittest.main(verbosity=2)

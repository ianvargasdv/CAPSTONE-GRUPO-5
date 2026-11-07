import json
import tempfile
import unittest
from datetime import datetime, date, timezone
from pathlib import Path
from prueba_catalogo import database, models
from renovar_escenario import renovar


class RenovacionTest(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        self.db=database.SessionLocal()
        self.addCleanup(self.db.close)
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.ahora=datetime(2026,11,4,23,0,tzinfo=timezone.utc)
        self.demo=models.Lead(nombre='Cliente ficticio',email='prueba@example.test',es_demo=True)
        self.real=models.Lead(nombre='Registro manual',email='persona@example.test',es_demo=False)
        self.db.add_all([self.demo,self.real]); self.db.flush()
        self.manual=models.Tarea(lead_id=self.real.id,titulo='No modificar',fecha_limite=date(2020,1,1))
        self.db.add(self.manual)
        for i in range(12):
            self.db.add(models.Tarea(lead_id=self.demo.id,titulo='Repetida',fecha_limite=date(2020,1,1)))
        self.contacto=models.Interaccion(lead_id=self.demo.id,tipo='Llamada',notas='Nota manual que debe conservarse',fecha_creacion=self.ahora)
        self.db.add(self.contacto); self.db.commit()

    def test_plan_no_modifica_y_aplicar_exige_respaldo(self):
        resultado=renovar(self.db,self.ahora)
        self.assertEqual(resultado['tareas'],12)
        self.assertEqual(self.db.query(models.Tarea).filter_by(titulo='Repetida').count(),12)
        with self.assertRaises(ValueError): renovar(self.db,self.ahora,True)

    def test_fechas_variedad_respaldo_y_repeticion_segura(self):
        ingreso_original=self.demo.fecha_creacion
        resultado=renovar(self.db,self.ahora,True,self.tmp.name); self.db.commit()
        tareas=self.db.query(models.Tarea).filter_by(lead_id=self.demo.id).all()
        self.assertEqual(len({t.titulo for t in tareas}),12)
        self.assertEqual(resultado['vencidas'],0)
        self.assertTrue(all(t.fecha_limite>=date(2026,11,4) for t in tareas if t.estado!='Completada'))
        self.assertEqual(self.manual.titulo,'No modificar')
        self.assertEqual(self.manual.fecha_limite,date(2020,1,1))
        self.assertEqual(self.contacto.notas,'Nota manual que debe conservarse')
        self.assertEqual(self.demo.fecha_creacion,ingreso_original)
        respaldo=json.loads(Path(resultado['respaldo']).read_text(encoding='utf-8'))
        self.assertEqual(respaldo['tareas'][0]['titulo'],'Repetida')
        self.assertEqual(renovar(self.db,self.ahora,True,self.tmp.name),{'ya_aplicado':True})
        self.assertEqual(self.db.query(models.Auditoria).count(),1)

    def test_visitas_futuras_y_cierres_coherentes(self):
        visita=models.Visita(lead_id=self.demo.id,fecha_hora=self.ahora,estado='Programada',modalidad='Presencial')
        negocio=models.Oportunidad(lead_id=self.demo.id,tipo_operacion='Compra',etapa='Contacto')
        self.db.add_all([visita,negocio]); self.db.commit()
        renovar(self.db,self.ahora,True,self.tmp.name); self.db.flush()
        self.assertGreater(visita.fecha_hora,self.ahora)
        self.assertGreater(negocio.fecha_cierre_estimada,date(2026,11,4))
        self.assertIsNone(negocio.fecha_cierre)

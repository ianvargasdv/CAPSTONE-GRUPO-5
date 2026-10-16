"""Regresión de migración: sólo SQLite temporal y registros ficticios."""
from datetime import datetime, timezone, timedelta
import unittest
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine, select, text
from sqlalchemy.exc import IntegrityError
from consolidar_asignaciones import consolidar_historial


class ConsolidacionTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.meta = MetaData()
        self.usuarios = Table('usuarios', self.meta, Column('id', Integer, primary_key=True), Column('nombre', String(100)))
        self.leads = Table('leads', self.meta, Column('id', Integer, primary_key=True), Column('nombre', String(100)), Column('ejecutivo_id', Integer))
        self.destino = Table('asignaciones_lead', self.meta,
            Column('id', Integer, primary_key=True), Column('lead_id', Integer), Column('lead_nombre', String(100), nullable=False),
            Column('anterior_id', Integer), Column('anterior_nombre', String(100)), Column('nuevo_id', Integer),
            Column('nuevo_nombre', String(100), nullable=False), Column('autor_id', Integer), Column('autor_nombre', String(100), nullable=False),
            Column('autor_email', String(150)), Column('historial_origen_id', Integer, unique=True), Column('fecha_creacion', DateTime(timezone=True), nullable=False))
        self.origen = Table('historial_asignaciones', self.meta,
            Column('id', Integer, primary_key=True), Column('lead_id', Integer),
            Column('ejecutivo_anterior_id', Integer), Column('ejecutivo_anterior_nombre', String(100)),
            Column('ejecutivo_nuevo_id', Integer), Column('ejecutivo_nuevo_nombre', String(100)),
            Column('realizado_por_id', Integer), Column('realizado_por_email', String(150)), Column('fecha_creacion', DateTime(timezone=True)))
        self.meta.create_all(self.engine)
        self.fecha = datetime(2026, 10, 1, 12, 30, 5, 123456, tzinfo=timezone.utc)
        with self.engine.begin() as con:
            con.execute(self.usuarios.insert(), [{'id': 1, 'nombre': 'Autor actual'}, {'id': 2, 'nombre': 'Responsable actual'}])
            con.execute(self.leads.insert(), {'id': 1, 'nombre': 'Lead de prueba', 'ejecutivo_id': 2})

    def tearDown(self):
        self.engine.dispose()

    def agregar(self, **cambios):
        fila = dict(id=1, lead_id=1, ejecutivo_anterior_id=1, ejecutivo_anterior_nombre='Nombre anterior guardado',
            ejecutivo_nuevo_id=2, ejecutivo_nuevo_nombre='Nombre nuevo guardado', realizado_por_id=1,
            realizado_por_email='historico@example.test', fecha_creacion=self.fecha)
        fila.update(cambios)
        with self.engine.begin() as con: con.execute(self.origen.insert(), fila)

    def filas(self):
        with self.engine.connect() as con: return list(con.execute(select(self.destino)).mappings())

    def test_preserva_fechas_nombres_correo_y_original(self):
        self.agregar()
        with self.engine.begin() as con:
            anterior = con.execute(select(self.origen)).mappings().all()
            self.assertEqual(consolidar_historial(con), 1)
            self.assertEqual(con.execute(select(self.origen)).mappings().all(), anterior)
            self.assertEqual(con.execute(select(self.leads.c.ejecutivo_id)).scalar_one(), 2)
        fila = self.filas()[0]
        self.assertEqual(fila['fecha_creacion'], self.fecha.replace(tzinfo=None))
        self.assertEqual(fila['anterior_nombre'], 'Nombre anterior guardado')
        self.assertEqual(fila['nuevo_nombre'], 'Nombre nuevo guardado')
        self.assertEqual(fila['autor_email'], 'historico@example.test')
        self.assertEqual(fila['historial_origen_id'], 1)

    def test_repetir_no_duplica_y_admite_movimientos_posteriores(self):
        self.agregar()
        with self.engine.begin() as con:
            self.assertEqual(consolidar_historial(con), 1)
            self.assertEqual(consolidar_historial(con), 0)
        self.agregar(id=2, fecha_creacion=self.fecha + timedelta(days=1))
        with self.engine.begin() as con: self.assertEqual(consolidar_historial(con), 1)
        self.assertEqual(len(self.filas()), 2)

    def test_no_confunde_ids_locales_con_ids_de_origen(self):
        self.agregar()
        with self.engine.begin() as con:
            con.execute(self.destino.insert(), {'id': 1, 'lead_nombre': 'Otro lead', 'nuevo_nombre': 'Otro responsable', 'autor_nombre': 'Otro autor', 'fecha_creacion': self.fecha})
            self.assertEqual(consolidar_historial(con), 1)
        self.assertEqual(len(self.filas()), 2)

    def test_sin_tabla_anterior_no_requiere_reconstruir_nada(self):
        with self.engine.begin() as con:
            self.origen.drop(con)
            self.assertEqual(consolidar_historial(con), 0)

    def test_sin_registros_no_inventa_historial(self):
        with self.engine.begin() as con: self.assertEqual(consolidar_historial(con), 0)
        self.assertEqual(self.filas(), [])

    def test_fecha_ausente_rechaza_todo_el_lote(self):
        self.agregar()
        self.agregar(id=2, fecha_creacion=None)
        with self.assertRaisesRegex(ValueError, 'sin fecha'):
            with self.engine.begin() as con: consolidar_historial(con)
        self.assertEqual(self.filas(), [])

    def test_texto_largo_no_se_trunca_ni_importa_parcialmente(self):
        self.agregar()
        self.agregar(id=2, ejecutivo_nuevo_nombre='x' * 101)
        with self.assertRaisesRegex(ValueError, 'no se truncará'):
            with self.engine.begin() as con: consolidar_historial(con)
        self.assertEqual(self.filas(), [])

    def test_correo_largo_valido_se_conserva(self):
        correo = 'a' * 130 + '@example.test'
        self.agregar(realizado_por_email=correo)
        with self.engine.begin() as con: self.assertEqual(consolidar_historial(con), 1)
        self.assertEqual(self.filas()[0]['autor_email'], correo)

    def test_cuentas_eliminadas_no_producen_ids_colgantes(self):
        self.agregar(lead_id=999, ejecutivo_anterior_id=998, ejecutivo_nuevo_id=997, realizado_por_id=996)
        with self.engine.begin() as con: self.assertEqual(consolidar_historial(con), 1)
        fila = self.filas()[0]
        for campo in ['lead_id', 'anterior_id', 'nuevo_id', 'autor_id']: self.assertIsNone(fila[campo])
        self.assertEqual(fila['nuevo_nombre'], 'Nombre nuevo guardado')
        self.assertEqual(fila['autor_email'], 'historico@example.test')

    def test_datos_ausentes_se_indican_sin_inventar_nombres(self):
        self.agregar(ejecutivo_anterior_id=None, ejecutivo_anterior_nombre=None,
            ejecutivo_nuevo_id=None, ejecutivo_nuevo_nombre=None, realizado_por_id=None, realizado_por_email=None)
        with self.engine.begin() as con: self.assertEqual(consolidar_historial(con), 1)
        fila = self.filas()[0]
        self.assertIsNone(fila['anterior_nombre'])
        self.assertEqual(fila['nuevo_nombre'], 'Nombre no registrado')
        self.assertEqual(fila['autor_nombre'], 'Autor no registrado')

    def test_estructura_incompatible_se_rechaza(self):
        with self.engine.begin() as con:
            self.origen.drop(con)
            con.execute(text('CREATE TABLE historial_asignaciones (id INTEGER PRIMARY KEY)'))
            with self.assertRaisesRegex(ValueError, 'estructura esperada'): consolidar_historial(con)

    def test_indice_unico_rechaza_segunda_copia_del_origen(self):
        self.agregar()
        with self.engine.begin() as con: consolidar_historial(con)
        fila = dict(self.filas()[0]); del fila['id']
        with self.assertRaises(IntegrityError):
            with self.engine.begin() as con: con.execute(self.destino.insert(), fila)


if __name__ == '__main__': unittest.main(verbosity=2)

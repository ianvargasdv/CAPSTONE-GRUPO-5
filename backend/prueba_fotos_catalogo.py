import unittest
from prueba_catalogo import database, models
from fotos_catalogo import asignar, catalogo


class FotosCatalogoTest(unittest.TestCase):
    def test_carga_por_tipo_conserva_fotos_y_no_repite_auditoria(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        with database.SessionLocal() as db:
            nuevas = [models.Propiedad(titulo='Propiedad de prueba', tipo=t, precio=1, direccion='Referencia')
                      for t in ('Departamento', 'Casa', 'Terreno')]
            existente = models.Propiedad(titulo='Con foto', tipo='Casa', precio=1, direccion='Referencia',
                                        fotografias=['https://example.test/real.jpg'], foto_principal='https://example.test/real.jpg')
            db.add_all([*nuevas, existente]); db.commit()
            fotos = catalogo()
            ids = asignar(db, fotos); db.commit()
            self.assertEqual(ids, [nuevas[0].id, nuevas[1].id])
            self.assertEqual(nuevas[0].foto_principal, fotos['Departamento'][0])
            self.assertEqual(nuevas[1].fotografias, [fotos['Casa'][0]])
            self.assertEqual(existente.foto_principal, 'https://example.test/real.jpg')
            self.assertEqual(asignar(db, fotos), [])
            self.assertEqual(db.query(models.Auditoria).count(), 2)
            self.assertIsNone(db.query(models.Auditoria).first().usuario_id)

    def test_no_reemplaza_principal_aunque_la_galeria_este_vacia(self):
        models.Base.metadata.drop_all(database.engine)
        models.Base.metadata.create_all(database.engine)
        with database.SessionLocal() as db:
            p = models.Propiedad(titulo='Principal existente', tipo='Casa', precio=1, direccion='Referencia',
                                 foto_principal='https://example.test/conservar.jpg')
            db.add(p); db.commit()
            self.assertEqual(asignar(db, catalogo()), [])
            self.assertEqual(p.foto_principal, 'https://example.test/conservar.jpg')

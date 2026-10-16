"""Nombres naturales para registros ficticios, conservando su origen y auditoría.

Sin --aplicar sólo muestra conteos. No modifica textos históricos ni elimina filas.
"""
import argparse
import re

MARCA_LEGADO = 'Registro ficticio del escenario inicial.'


def nombre_natural(valor):
    limpio = re.sub(r'\s*\(demo\)\s*$', '', valor or '', flags=re.IGNORECASE).strip()
    return limpio or valor


def titulo_natural(valor):
    limpio = re.sub(r'^\s*\[demo\]\s*', '', valor or '', flags=re.IGNORECASE).strip()
    return limpio or valor


def normalizar(aplicar=False):
    import database
    import models
    conteos = {'leads':0,'propiedades':0}
    with database.SessionLocal() as db:
        try:
            for lead in db.query(models.Lead).filter(models.Lead.es_demo.is_(True)).all():
                cambios = {}
                nuevo = nombre_natural(lead.nombre)
                if nuevo != lead.nombre: cambios['nombre'] = nuevo
                if lead.origen == 'Demo capstone': cambios['origen'] = 'Escenario de prueba'
                if not cambios: continue
                conteos['leads'] += 1
                if aplicar:
                    for campo,valor in cambios.items(): setattr(lead,campo,valor)
                    db.add(models.Auditoria(accion='actualizar',entidad='lead',entidad_id=lead.id,
                        descripcion='Normalizó la presentación de un cliente ficticio',
                        detalle='Se mantienen su identificador, relaciones y marca interna de prueba. Campos: '+', '.join(cambios)))
            for propiedad in db.query(models.Propiedad).all():
                nuevo = titulo_natural(propiedad.titulo)
                if nuevo == propiedad.titulo: continue
                conteos['propiedades'] += 1
                if aplicar:
                    propiedad.titulo = nuevo
                    if not (propiedad.descripcion or '').startswith(MARCA_LEGADO):
                        propiedad.descripcion = MARCA_LEGADO+' '+(propiedad.descripcion or '')
                    db.add(models.Auditoria(accion='actualizar',entidad='propiedad',entidad_id=propiedad.id,
                        descripcion='Normalizó la presentación de una propiedad ficticia',
                        detalle='Se conserva su identificador, ficha y relaciones. El origen ficticio consta en la descripción.'))
            if aplicar: db.commit()
            else: db.rollback()
        except Exception:
            db.rollback()
            raise
    return conteos


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar',action='store_true')
    args = parser.parse_args()
    try:
        print(('Registros normalizados: ' if args.aplicar else 'Vista previa, sin cambios: ')+str(normalizar(args.aplicar)))
    except Exception:
        print('No se completó la normalización; se revirtieron los cambios de esta ejecución.')
        raise SystemExit(1)

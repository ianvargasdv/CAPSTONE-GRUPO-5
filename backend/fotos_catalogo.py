"""Carga explícita de enlaces referenciales; no reemplaza fotografías existentes."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen


def catalogo():
    datos = json.loads((Path(__file__).parent / 'recursos' / 'fotos_catalogo.json').read_text(encoding='utf-8'))
    return {tipo: [f'https://images.pexels.com/photos/{foto}/pexels-photo-{foto}.jpeg?auto=compress&cs=tinysrgb&w=960#referencial'
                   for foto in datos[tipo]] for tipo in ('Departamento', 'Casa')}


def asignar(db, fotos):
    import models
    import auditoria
    cantidades = {tipo: 0 for tipo in fotos}
    cambios = []
    for p in db.query(models.Propiedad).order_by(models.Propiedad.id).with_for_update().all():
        if p.fotografias or p.foto_principal or not fotos.get(p.tipo):
            continue
        opciones = fotos[p.tipo]
        url = opciones[cantidades[p.tipo] % len(opciones)]
        cantidades[p.tipo] += 1
        p.fotografias = [url]
        p.foto_principal = url
        auditoria.registrar(db, None, auditoria.ACTUALIZAR, auditoria.PROPIEDAD, p.id,
                           'Carga de fotografía referencial del catálogo',
                           f'fotografias: [] -> [{url}]; foto_principal: vacío -> {url}; fuente: Pexels; imagen referencial')
        cambios.append(p.id)
    return cambios


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true', help='Guardar enlaces y auditoría en la base configurada.')
    args = parser.parse_args()
    import database
    import models
    fotos = catalogo()
    with database.SessionLocal() as db:
        candidatas = [p.id for p in db.query(models.Propiedad).all()
                      if not p.fotografias and not p.foto_principal and p.tipo in fotos]
    print(json.dumps({'propiedades_sin_fotos': candidatas, 'cantidad': len(candidatas)}))
    if not args.aplicar or not candidatas:
        return
    # Verificar los destinos antes de adquirir bloqueos o cambiar la base.
    from concurrent.futures import ThreadPoolExecutor
    def verificar(url):
        req = Request(url.split('#')[0], headers={'User-Agent': 'CRM-catalogo/1.0'})
        with urlopen(req, timeout=25) as respuesta:
            if not respuesta.headers.get('Content-Type', '').startswith('image/'):
                raise ValueError('El enlace no devuelve una imagen')
            if len(respuesta.read(2_000_001)) > 2_000_000:
                raise ValueError('La imagen supera el límite de revisión')
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(verificar, [url for lista in fotos.values() for url in lista]))
    with database.SessionLocal() as db:
        try:
            ids = asignar(db, fotos)
            db.commit()
        except Exception:
            db.rollback()
            raise
    print(json.dumps({'propiedades_actualizadas': ids, 'cantidad': len(ids), 'almacenado': 'Sólo enlaces, sin archivos binarios'}))


if __name__ == '__main__':
    main()

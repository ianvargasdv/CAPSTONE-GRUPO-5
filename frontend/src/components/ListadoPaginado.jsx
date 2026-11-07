import React, { useState } from 'react';
import { paginar } from '../paginacion';

export default function ListadoPaginado({ items, children, etiqueta = 'registros' }) {
  const [pagina, setPagina] = useState(1);
  const [tamano, setTamano] = useState(10);
  const datos = paginar(items, pagina, tamano);
  return <>
    {children(datos.items)}
    <nav className="listado-paginacion" aria-label={`Páginas de ${etiqueta}`}>
      <span role="status">{datos.desde}–{datos.hasta} de {items.length} {etiqueta}</span>
      <label>Por página <select value={tamano} onChange={e => { setTamano(Number(e.target.value)); setPagina(1); }}>
        {[10, 25, 50].map(n => <option key={n} value={n}>{n}</option>)}
      </select></label>
      <div><button className="btn-secondary" disabled={datos.actual === 1} onClick={() => setPagina(datos.actual - 1)}>Anterior</button>
        <span>Página {datos.actual} de {datos.paginas}</span>
        <button className="btn-secondary" disabled={datos.actual === datos.paginas} onClick={() => setPagina(datos.actual + 1)}>Siguiente</button></div>
    </nav>
  </>;
}

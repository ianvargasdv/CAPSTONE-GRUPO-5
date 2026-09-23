import React, { useEffect } from 'react';
import Icono from './Iconos';

/**
 * Panel lateral deslizante. Se usa para crear y editar registros, y para ver la ficha de un lead.
 *
 * Reemplaza el patrón de tener formularios siempre visibles sobre las tablas:
 * el listado queda como vista principal y la edición ocurre en este panel.
 *
 * Props:
 * - abierto: controla la visibilidad
 * - titulo: título del panel
 * - subtitulo: texto secundario opcional bajo el título
 * - ancho: si es true usa el ancho amplio (para la ficha del lead)
 * - alCerrar: función llamada al cerrar (overlay, botón o tecla Escape)
 * - children: contenido del panel
 */
function Drawer({ abierto, titulo, subtitulo, ancho = false, alCerrar, children }) {
  // Cierra con la tecla Escape y bloquea el scroll del fondo mientras está abierto
  useEffect(() => {
    if (!abierto) return;

    const manejarTecla = (e) => {
      if (e.key === 'Escape') alCerrar();
    };

    document.addEventListener('keydown', manejarTecla);
    const overflowOriginal = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', manejarTecla);
      document.body.style.overflow = overflowOriginal;
    };
  }, [abierto, alCerrar]);

  if (!abierto) return null;

  return (
    <>
      <div className="drawer-overlay" onClick={alCerrar} />

      <aside
        className={`drawer ${ancho ? 'ancho' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
      >
        <div className="drawer-encabezado">
          <div>
            <h2 className="drawer-titulo">{titulo}</h2>
            {subtitulo && <p className="drawer-subtitulo">{subtitulo}</p>}
          </div>
          <button className="btn-icono" onClick={alCerrar} title="Cerrar (Esc)">
            <Icono nombre="cerrar" />
          </button>
        </div>

        <div className="drawer-cuerpo">{children}</div>
      </aside>
    </>
  );
}

export default Drawer;

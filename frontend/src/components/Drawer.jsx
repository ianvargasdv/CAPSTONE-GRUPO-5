import React, { useEffect, useRef } from 'react';
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
  const panel = useRef(null);
  const cerrarActual = useRef(alCerrar);
  const ultimoFocoExterno = useRef(null);
  cerrarActual.current = alCerrar;
  useEffect(() => {
    const recordarFoco = (evento) => {
      if (evento.type === 'keydown' && !['Enter', ' '].includes(evento.key)) return;
      if (!panel.current?.contains(evento.target)) {
        const control = evento.target.closest?.('button, a[href], input, select, textarea, [tabindex]');
        if (control) ultimoFocoExterno.current = control;
      }
    };
    // Se recuerda el disparador antes del autoFocus de los campos del formulario.
    document.addEventListener('pointerdown', recordarFoco, true);
    document.addEventListener('keydown', recordarFoco, true);
    return () => {
      document.removeEventListener('pointerdown', recordarFoco, true);
      document.removeEventListener('keydown', recordarFoco, true);
    };
  }, []);
  // Cierra con la tecla Escape y bloquea el scroll del fondo mientras está abierto
  useEffect(() => {
    if (!abierto) return;
    const elementoAnterior = ultimoFocoExterno.current || document.activeElement;
    const controles = () => [...(panel.current?.querySelectorAll(
      'button, input, select, textarea, a[href], summary, [tabindex]:not([tabindex="-1"])'
    ) || [])].filter((el) => !el.matches(':disabled') && el.getClientRects().length > 0);
    if (!panel.current?.contains(document.activeElement)) {
      (controles()[0] || panel.current)?.focus();
    }

    const manejarTecla = (e) => {
      if (e.key === 'Escape' && !e.defaultPrevented) cerrarActual.current();
      if (e.key !== 'Tab') return;
      const elementos = controles();
      const primero = elementos[0];
      const ultimo = elementos.at(-1);
      if (!primero) { e.preventDefault(); panel.current?.focus(); return; }
      if (!panel.current?.contains(document.activeElement) ||
          (e.shiftKey && document.activeElement === primero) ||
          (!e.shiftKey && document.activeElement === ultimo)) {
        e.preventDefault();
        (e.shiftKey ? ultimo : primero).focus();
      }
    };

    document.addEventListener('keydown', manejarTecla);
    const overflowOriginal = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', manejarTecla);
      document.body.style.overflow = overflowOriginal;
      if (elementoAnterior?.isConnected && !panel.current?.contains(elementoAnterior)) {
        elementoAnterior.focus();
      }
    };
  }, [abierto]);

  if (!abierto) return null;

  return (
    <>
      <div className="drawer-overlay" onClick={alCerrar} />

      <aside
        ref={panel}
        tabIndex={-1}
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
          <button className="btn-icono" onClick={alCerrar} title="Cerrar (Esc)" aria-label="Cerrar panel">
            <Icono nombre="cerrar" />
          </button>
        </div>

        <div className="drawer-cuerpo">{children}</div>
      </aside>
    </>
  );
}

export default Drawer;

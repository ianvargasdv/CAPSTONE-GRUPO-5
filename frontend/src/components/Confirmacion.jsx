import React, { useEffect } from 'react';

/**
 * Modal de confirmación para acciones destructivas.
 *
 * Reemplaza window.confirm() del navegador, que no se puede estilizar
 * y rompe visualmente con el resto de la interfaz.
 *
 * Props:
 * - abierto: controla la visibilidad
 * - titulo: encabezado del modal
 * - mensaje: texto explicativo de la acción
 * - textoConfirmar: etiqueta del botón de acción (por defecto "Eliminar")
 * - procesando: deshabilita los botones mientras se ejecuta la acción
 * - alConfirmar: función llamada al confirmar
 * - alCancelar: función llamada al cancelar (overlay, botón o Escape)
 */
function Confirmacion({
  abierto,
  titulo,
  mensaje,
  textoConfirmar = 'Eliminar',
  procesando = false,
  alConfirmar,
  alCancelar,
}) {
  useEffect(() => {
    if (!abierto) return;

    const manejarTecla = (e) => {
      if (e.key === 'Escape' && !procesando) alCancelar();
    };

    document.addEventListener('keydown', manejarTecla);
    return () => document.removeEventListener('keydown', manejarTecla);
  }, [abierto, procesando, alCancelar]);

  if (!abierto) return null;

  return (
    <div
      className="modal-overlay"
      onClick={() => {
        if (!procesando) alCancelar();
      }}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="modal-titulo">{titulo}</h2>
        <p className="modal-texto">{mensaje}</p>

        <div className="modal-acciones">
          <button
            className="btn-secondary"
            onClick={alCancelar}
            disabled={procesando}
          >
            Cancelar
          </button>
          <button
            className="btn-primary btn-peligro"
            onClick={alConfirmar}
            disabled={procesando}
          >
            {procesando ? 'Eliminando...' : textoConfirmar}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Confirmacion;

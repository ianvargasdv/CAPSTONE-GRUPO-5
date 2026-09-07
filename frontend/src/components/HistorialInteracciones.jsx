import React from 'react';

/**
 * Muestra el historial de interacciones de un lead en orden cronológico inverso.
 *
 * Props:
 * - interacciones: lista de interacciones del lead
 * - cargando: boolean que indica si los datos están cargando
 * - error: mensaje de error si la carga falló
 */

// Mapa de íconos de texto por tipo de interacción
const ICONO_TIPO = {
  Llamada: '📞',
  Email: '✉️',
  Visita: '🏠',
  WhatsApp: '💬',
};

function HistorialInteracciones({ interacciones, cargando, error }) {
  if (cargando) {
    return <div className="state-message">Cargando historial...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!interacciones || interacciones.length === 0) {
    return (
      <div className="state-message empty">
        No hay interacciones registradas para este lead.
      </div>
    );
  }

  return (
    <div className="historial-lista">
      {interacciones.map((interaccion) => (
        <div key={interaccion.id} className="historial-item">
          <div className="historial-icono">
            {ICONO_TIPO[interaccion.tipo] || '📋'}
          </div>
          <div className="historial-contenido">
            <div className="historial-encabezado">
              <span className="historial-tipo">{interaccion.tipo}</span>
              <span className="historial-fecha">
                {interaccion.fecha_creacion
                  ? new Date(interaccion.fecha_creacion).toLocaleDateString('es-CL', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })
                  : '-'}
              </span>
            </div>
            {interaccion.notas && (
              <p className="historial-notas">{interaccion.notas}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default HistorialInteracciones;

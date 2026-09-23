import React from 'react';
import Icono from './Iconos';

/**
 * Línea de tiempo con el historial de contacto de un lead, del más reciente al más antiguo.
 *
 * Props:
 * - interacciones: lista de interacciones del lead
 * - cargando / error: estado de la carga
 */

// Cada tipo de contacto tiene su propio icono para poder recorrer el historial de un vistazo
const ICONO_TIPO = {
  Llamada: 'telefono',
  Email: 'correo',
  Visita: 'casa',
  WhatsApp: 'mensaje',
};

function HistorialInteracciones({ interacciones, cargando, error }) {
  if (cargando) {
    return <div className="state-message">Cargando historial...</div>;
  }

  if (error) {
    return (
      <div className="alert-error">
        <Icono nombre="alerta" />
        <span>{error}</span>
      </div>
    );
  }

  if (!interacciones || interacciones.length === 0) {
    return (
      <div className="state-message empty">
        <span className="vacio-titulo">Sin interacciones registradas</span>
        <span className="vacio-detalle">
          Registra la primera llamada, visita o correo para empezar el historial.
        </span>
      </div>
    );
  }

  return (
    <ul className="historial-lista">
      {interacciones.map((interaccion) => (
        <li key={interaccion.id} className="historial-item">
          <div className="historial-marcador">
            <Icono nombre={ICONO_TIPO[interaccion.tipo] || 'mensaje'} tamano={13} />
          </div>

          <div className="historial-contenido">
            <div className="historial-encabezado">
              <span className="historial-tipo">{interaccion.tipo}</span>
              <span className="historial-fecha">
                {interaccion.fecha_creacion
                  ? new Date(interaccion.fecha_creacion).toLocaleString('es-CL', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })
                  : '—'}
              </span>
            </div>

            {interaccion.notas && <p className="historial-notas">{interaccion.notas}</p>}
          </div>
        </li>
      ))}
    </ul>
  );
}

export default HistorialInteracciones;

import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Sección de la ficha del lead que gestiona la asignación de ejecutivo.
 *
 * Muestra quién tiene el lead a cargo, un selector para asignar o reasignar, y el
 * historial completo de cambios. El estado de carga y los errores los maneja
 * localmente para el selector; el historial llega ya cargado desde App.jsx.
 *
 * Props:
 * - lead             objeto lead con ejecutivo_id y ejecutivo (EjecutivoResumen | null)
 * - ejecutivos       lista de usuarios activos disponibles para asignar
 * - historial        registros de HistorialAsignacionRespuesta
 * - cargandoHistorial estado de carga del historial
 * - errorHistorial    mensaje de error si no se pudo cargar el historial
 * - alAsignar(ejecutivoId)  callback que recibe el id (o null para quitar asignación)
 */

/** Fecha y hora en formato local corto. */
function fechaCorta(valor) {
  if (!valor) return '—';
  return new Date(valor).toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function AsignacionLead({
  lead,
  ejecutivos,
  historial,
  cargandoHistorial,
  errorHistorial,
  alAsignar,
}) {
  const [seleccionado, setSeleccionado] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState(null);
  const [expandirHistorial, setExpandirHistorial] = useState(false);

  /**
   * Se inicializa el selector con el ejecutivo actual cuando el componente recibe
   * un nuevo lead (cambia la ficha abierta). El valor vacío representa "sin asignar".
   */
  const valorSelector = seleccionado !== '' ? seleccionado : String(lead.ejecutivo_id ?? '');

  const confirmarAsignacion = async () => {
    // El valor del selector es siempre un string; convertir a número o null
    const nuevoId = valorSelector === '' ? null : Number(valorSelector);

    // Si no cambió nada, no tiene sentido llamar al backend
    if (nuevoId === (lead.ejecutivo_id ?? null)) return;

    try {
      setGuardando(true);
      setError(null);
      await alAsignar(nuevoId);
      setSeleccionado('');    // resetear selector: el lead.ejecutivo_id se actualizó
    } catch (err) {
      setError(err.message || 'No se pudo guardar la asignación');
    } finally {
      setGuardando(false);
    }
  };

  // El valor actual del selector determina si hubo un cambio real
  const idActual = lead.ejecutivo_id ?? null;
  const idSelector = valorSelector === '' ? null : Number(valorSelector);
  const cambio = idSelector !== idActual;

  return (
    <div>
      <div className="ficha-seccion-encabezado">
        <span className="ficha-seccion-titulo">Ejecutivo responsable</span>
        {historial.length > 0 && (
          <button
            className="btn-icono"
            onClick={() => setExpandirHistorial((v) => !v)}
            title={expandirHistorial ? 'Ocultar historial' : 'Ver historial de asignaciones'}
            aria-expanded={expandirHistorial}
          >
            <Icono nombre="historial" tamano={14} />
          </button>
        )}
      </div>

      {/* ── Selector de asignación ── */}
      <div className="asignacion-selector">
        <select
          className="filter-select asignacion-select"
          value={valorSelector}
          onChange={(e) => setSeleccionado(e.target.value)}
          disabled={guardando}
          aria-label="Seleccionar ejecutivo responsable"
        >
          <option value="">Sin asignar</option>
          {ejecutivos.map((ej) => (
            <option key={ej.id} value={String(ej.id)}>
              {ej.nombre}
            </option>
          ))}
        </select>

        <button
          className="btn-primary"
          onClick={confirmarAsignacion}
          disabled={!cambio || guardando}
          aria-busy={guardando}
        >
          {guardando ? 'Guardando…' : lead.ejecutivo_id ? 'Reasignar' : 'Asignar'}
        </button>
      </div>

      {error && (
        <div className="alert-error" style={{ marginTop: '0.5rem' }}>
          <Icono nombre="alerta" tamano={13} />
          <span>{error}</span>
        </div>
      )}

      {/* ── Historial de asignaciones ── */}
      {expandirHistorial && (
        <div className="historial-asignaciones" aria-live="polite">
          {cargandoHistorial && (
            <div className="state-message">Cargando historial…</div>
          )}

          {errorHistorial && !cargandoHistorial && (
            <div className="alert-error">
              <Icono nombre="alerta" tamano={13} />
              <span>{errorHistorial}</span>
            </div>
          )}

          {!cargandoHistorial && !errorHistorial && historial.length === 0 && (
            <p className="nota-prioridad">Todavía no hay cambios de asignación registrados.</p>
          )}

          {!cargandoHistorial && historial.length > 0 && (
            <ol className="historial-lista" aria-label="Historial de asignaciones">
              {historial.map((entrada, indice) => {
                const esPrimera = entrada.ejecutivo_anterior_id === null
                  && entrada.ejecutivo_anterior_nombre === null;

                return (
                  <li key={entrada.id} className="historial-entrada">
                    <div className="historial-linea-tiempo">
                      <span
                        className={`historial-punto ${indice === 0 ? 'historial-punto--actual' : ''}`}
                        aria-hidden="true"
                      />
                      {indice < historial.length - 1 && (
                        <span className="historial-conector" aria-hidden="true" />
                      )}
                    </div>

                    <div className="historial-contenido">
                      <div className="historial-encabezado">
                        <span className={`etiqueta ${esPrimera ? 'exito' : 'info'}`}>
                          {esPrimera ? 'Primera asignación' : 'Reasignación'}
                        </span>
                        <span className="historial-fecha">{fechaCorta(entrada.fecha_creacion)}</span>
                      </div>

                      <div className="historial-cambio">
                        {!esPrimera && (
                          <>
                            <span className="historial-nombre historial-nombre--anterior">
                              {entrada.ejecutivo_anterior_nombre ?? <em>sin asignar</em>}
                            </span>
                            <Icono nombre="chevron" tamano={12} className="historial-flecha" />
                          </>
                        )}
                        <span className="historial-nombre historial-nombre--nuevo">
                          {entrada.ejecutivo_nuevo_nombre ?? <em>sin asignar</em>}
                        </span>
                      </div>

                      {entrada.realizado_por_email && (
                        <span className="historial-autor">
                          por {entrada.realizado_por_email}
                        </span>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </div>
      )}
    </div>
  );
}

export default AsignacionLead;

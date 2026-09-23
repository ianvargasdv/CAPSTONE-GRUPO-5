import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Sección de la ficha que muestra el resumen del lead generado por el modelo de
 * lenguaje.
 *
 * Dos cosas deliberadas en el diseño:
 *
 * 1. El texto siempre aparece identificado como generado automáticamente, con la
 *    fecha y el modelo que lo produjo. No debe poder confundirse con una nota que
 *    escribió una persona.
 *
 * 2. Se puede desplegar la información exacta que recibió el modelo. Sirve para
 *    verificar que el resumen se apoya en los registros del CRM y no en algo que
 *    el modelo agregó por su cuenta.
 *
 * Props:
 * - analisis: lista de análisis del lead, del más reciente al más antiguo
 * - cargando / error: estado de la carga
 * - iaConfigurada: si el backend tiene proveedor de IA configurado
 * - alGenerar: pide un resumen nuevo, devuelve una promesa
 */
function ResumenIA({ analisis = [], cargando, error, iaConfigurada, alGenerar }) {
  const [generando, setGenerando] = useState(false);
  const [errorGeneracion, setErrorGeneracion] = useState(null);

  const ultimo = analisis[0];

  const manejarGenerar = async () => {
    try {
      setGenerando(true);
      setErrorGeneracion(null);
      await alGenerar();
    } catch (err) {
      setErrorGeneracion(err.message || 'No se pudo generar el resumen');
    } finally {
      setGenerando(false);
    }
  };

  const fechaLarga = (iso) =>
    new Date(iso).toLocaleString('es-CL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

  return (
    <>
      <div className="ficha-seccion-encabezado">
        <span className="ficha-seccion-titulo">Resumen del agente</span>

        {iaConfigurada && (
          <button className="btn-secondary" onClick={manejarGenerar} disabled={generando}>
            {generando ? (
              'Generando...'
            ) : (
              <>
                <Icono nombre="mas" tamano={13} />
                {ultimo ? 'Generar de nuevo' : 'Generar resumen'}
              </>
            )}
          </button>
        )}
      </div>

      {errorGeneracion && (
        <div className="alert-error" style={{ marginBottom: '0.75rem' }}>
          <Icono nombre="alerta" />
          <span>{errorGeneracion}</span>
        </div>
      )}

      {!iaConfigurada ? (
        <div className="state-message empty">
          <span className="vacio-titulo">Servicio de IA sin configurar</span>
          <span className="vacio-detalle">
            Para generar resúmenes hay que completar IA_BASE_URL e IA_MODELO en el
            archivo .env del backend. El resto del sistema funciona igual sin esto.
          </span>
        </div>
      ) : generando ? (
        <div className="bloque-resumen generando">
          <p className="resumen-esperando">
            Consultando al modelo. Puede tardar unos segundos.
          </p>
        </div>
      ) : cargando ? (
        <div className="state-message">Cargando resúmenes...</div>
      ) : error ? (
        <div className="alert-error">
          <Icono nombre="alerta" />
          <span>{error}</span>
        </div>
      ) : !ultimo ? (
        <div className="state-message empty">
          <span className="vacio-titulo">Sin resumen generado</span>
          <span className="vacio-detalle">
            El resumen se arma con los datos registrados del lead: su historial de
            contacto, sus propiedades de interés y su prioridad calculada.
          </span>
        </div>
      ) : (
        <div className="bloque-resumen">
          <p className="resumen-texto">{ultimo.salida}</p>

          <div className="resumen-pie">
            <span className="resumen-origen">
              <Icono nombre="alerta" tamano={11} />
              Generado automáticamente
            </span>
            <span className="resumen-meta">
              {fechaLarga(ultimo.fecha_creacion)}
              {ultimo.modelo && ` · ${ultimo.modelo}`}
            </span>
          </div>

          {ultimo.entrada && (
            <details className="resumen-detalle">
              <summary>Ver los datos que recibió el modelo</summary>
              <pre className="resumen-entrada">{ultimo.entrada}</pre>
            </details>
          )}

          {analisis.length > 1 && (
            <p className="resumen-anteriores">
              Hay {analisis.length - 1} resumen
              {analisis.length - 1 !== 1 ? 'es' : ''} anterior
              {analisis.length - 1 !== 1 ? 'es' : ''} guardado
              {analisis.length - 1 !== 1 ? 's' : ''}.
            </p>
          )}
        </div>
      )}
    </>
  );
}

export default ResumenIA;

import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Sección de la ficha con los dos análisis que produce el modelo de lenguaje:
 * un resumen de la situación del prospecto y una recomendación de la siguiente
 * acción a tomar.
 *
 * Tres cosas deliberadas en el diseño:
 *
 * 1. Cada texto aparece identificado como generado automáticamente, con la fecha y
 *    el modelo que lo produjo. No debe poder confundirse con una nota que escribió
 *    una persona.
 *
 * 2. Se puede desplegar la información exacta que recibió el modelo, para verificar
 *    que la respuesta se apoya en los registros del CRM y no en algo inventado.
 *
 * 3. Cada generación es un clic explícito. Nada se genera al abrir la ficha, porque
 *    cada llamada al proveedor cuesta.
 *
 * Props:
 * - analisis: lista de análisis del lead, del más reciente al más antiguo
 * - cargando / error: estado de la carga
 * - iaConfigurada: si el backend tiene proveedor de IA configurado
 * - alGenerar: recibe el tipo y devuelve una promesa
 */

const TEXTOS = {
  resumen: {
    titulo: 'Resumen de la situación',
    vacio: 'Describe en qué punto está el prospecto según su historial registrado.',
    boton: 'Generar resumen',
  },
  recomendacion: {
    titulo: 'Siguiente acción recomendada',
    vacio: 'Propone qué hacer con este prospecto, considerando sus tareas pendientes.',
    boton: 'Generar recomendación',
  },
};

function fechaLarga(iso) {
  return new Date(iso).toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function AsistenteIA({ analisis = [], cargando, error, iaConfigurada, alGenerar }) {
  // Guarda qué tipo se está generando, para deshabilitar solo ese botón
  const [generandoTipo, setGenerandoTipo] = useState(null);
  const [errorPorTipo, setErrorPorTipo] = useState({});

  const manejarGenerar = async (tipo) => {
    try {
      setGenerandoTipo(tipo);
      setErrorPorTipo((prev) => ({ ...prev, [tipo]: null }));
      await alGenerar(tipo);
    } catch (err) {
      const mensaje = err.message || 'No se pudo generar el análisis';
      setErrorPorTipo((prev) => ({ ...prev, [tipo]: mensaje }));
    } finally {
      setGenerandoTipo(null);
    }
  };

  if (!iaConfigurada) {
    return (
      <>
        <div className="ficha-seccion-encabezado">
          <span className="ficha-seccion-titulo">Asistente</span>
        </div>
        <div className="state-message empty">
          <span className="vacio-titulo">Servicio de IA sin configurar</span>
          <span className="vacio-detalle">
            Para generar resúmenes y recomendaciones hay que completar IA_BASE_URL e
            IA_MODELO en el archivo .env del backend. El resto del sistema funciona
            igual sin esto.
          </span>
        </div>
      </>
    );
  }

  if (cargando) {
    return (
      <>
        <div className="ficha-seccion-encabezado">
          <span className="ficha-seccion-titulo">Asistente</span>
        </div>
        <div className="state-message">Cargando análisis...</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <div className="ficha-seccion-encabezado">
          <span className="ficha-seccion-titulo">Asistente</span>
        </div>
        <div className="alert-error">
          <Icono nombre="alerta" />
          <span>{error}</span>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="ficha-seccion-encabezado">
        <span className="ficha-seccion-titulo">Asistente</span>
      </div>

      <div className="asistente-bloques">
        {['resumen', 'recomendacion'].map((tipo) => {
          // El backend devuelve los análisis del más reciente al más antiguo,
          // así que el primero de cada tipo es el vigente
          const ultimo = analisis.find((a) => a.tipo === tipo);
          const anteriores = analisis.filter((a) => a.tipo === tipo).length - 1;
          const generando = generandoTipo === tipo;
          const errorTipo = errorPorTipo[tipo];
          const textos = TEXTOS[tipo];

          return (
            <div key={tipo} className="asistente-bloque">
              <div className="asistente-encabezado">
                <span className="asistente-titulo">{textos.titulo}</span>
                <button
                  className="btn-secondary"
                  onClick={() => manejarGenerar(tipo)}
                  disabled={generandoTipo !== null}
                >
                  {generando ? (
                    'Generando...'
                  ) : (
                    <>
                      <Icono nombre="mas" tamano={13} />
                      {ultimo ? 'Generar de nuevo' : textos.boton}
                    </>
                  )}
                </button>
              </div>

              {errorTipo && (
                <div className="alert-error">
                  <Icono nombre="alerta" />
                  <span>{errorTipo}</span>
                </div>
              )}

              {generando ? (
                <div className="bloque-resumen generando">
                  <p className="resumen-esperando">
                    Consultando al modelo. Puede tardar unos segundos.
                  </p>
                </div>
              ) : !ultimo ? (
                <div className="asistente-vacio">{textos.vacio}</div>
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

                  {anteriores > 0 && (
                    <p className="resumen-anteriores">
                      Hay {anteriores} versión{anteriores !== 1 ? 'es' : ''} anterior
                      {anteriores !== 1 ? 'es' : ''} guardada
                      {anteriores !== 1 ? 's' : ''}.
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

export default AsistenteIA;

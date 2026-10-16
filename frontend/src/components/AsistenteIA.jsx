import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Análisis del lead y borradores revisables. No se envían mensajes ni se
 * modifican los datos del lead desde este componente.
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
  mensaje: {
    titulo: 'Borrador de seguimiento',
    vacio: 'Prepara un mensaje con el contexto del cliente. Revísalo antes de usarlo.',
    boton: 'Preparar mensaje',
  },
  preguntas: {
    titulo: 'Preguntas para completar el perfil',
    vacio: 'Sugiere qué preguntar según la información comercial que falta.',
    boton: 'Preparar preguntas',
  },
};

function BorradorMensaje({ texto }) {
  const [borrador, setBorrador] = useState(texto);
  const [aviso, setAviso] = useState('');

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(borrador);
      setAviso('Texto copiado. No se ha enviado ningún mensaje.');
    } catch {
      setAviso('No se pudo copiar. Selecciona el texto y cópialo manualmente.');
    }
  };

  return (
    <div className="asistente-borrador">
      <label htmlFor="borrador-seguimiento">Revisar y editar el mensaje</label>
      <textarea id="borrador-seguimiento" className="form-textarea" rows={5}
        maxLength={4000} value={borrador}
        onChange={(e) => { setBorrador(e.target.value); setAviso(''); }} />
      <div className="asistente-borrador-acciones">
        <button className="btn-secondary" disabled={!borrador.trim()} onClick={copiar}>Copiar mensaje</button>
        <span>Edición temporal. No envía ni registra un contacto.</span>
      </div>
      {aviso && <p role="status" className="resumen-anteriores">{aviso}</p>}
    </div>
  );
}

function fechaLarga(iso) {
  return new Date(iso).toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Formatea el costo con suficientes decimales: son cifras muy chicas. */
function costoUSD(valor) {
  return valor.toLocaleString('es-CL', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 4,
    maximumFractionDigits: 6,
  });
}

function AsistenteIA({ analisis = [], cargando, error, iaConfigurada, alGenerar }) {
  // Evita generar dos análisis al mismo tiempo desde esta ficha.
  const [generandoTipo, setGenerandoTipo] = useState(null);
  const [errorPorTipo, setErrorPorTipo] = useState({});
  const [tipoActivo, setTipoActivo] = useState('resumen');

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
            Para usar el asistente hay que completar IA_BASE_URL e
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

      <div className="asistente-opciones" role="group" aria-label="Funciones del asistente">
        {Object.entries(TEXTOS).map(([tipo, textos]) => (
          <button key={tipo} className="btn-secondary" aria-pressed={tipoActivo === tipo}
            disabled={generandoTipo !== null} onClick={() => setTipoActivo(tipo)}>{textos.titulo}</button>
        ))}
      </div>
      <div className="asistente-bloques">
        {Object.keys(TEXTOS).map((tipo) => {
          // El backend devuelve los análisis del más reciente al más antiguo,
          // así que el primero de cada tipo es el vigente
          const ultimo = analisis.find((a) => a.tipo === tipo);
          const anteriores = analisis.filter((a) => a.tipo === tipo).length - 1;
          const generando = generandoTipo === tipo;
          const errorTipo = errorPorTipo[tipo];
          const textos = TEXTOS[tipo];

          return (
            <div key={tipo} className="asistente-bloque" hidden={tipoActivo !== tipo}>
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
                  {tipo === 'mensaje' ? (
                    <BorradorMensaje key={ultimo.id} texto={ultimo.salida} />
                  ) : (
                    <p className="resumen-texto">{ultimo.salida}</p>
                  )}

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

                  {/* Consumo de la llamada. Queda en nulo en los análisis generados
                      antes de que se empezara a registrar. */}
                  {(ultimo.tokens_entrada != null || ultimo.tokens_salida != null) && (
                    <div className="resumen-consumo">
                      <span>
                        {ultimo.tokens_entrada ?? 0} tokens enviados ·{' '}
                        {ultimo.tokens_salida ?? 0} recibidos
                      </span>
                      {ultimo.costo_estimado_usd != null && (
                        <span className="consumo-costo">
                          {costoUSD(ultimo.costo_estimado_usd)} estimados
                        </span>
                      )}
                    </div>
                  )}

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

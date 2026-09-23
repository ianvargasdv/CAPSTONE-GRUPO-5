import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Sección de la ficha del lead con las propiedades que le interesan.
 *
 * Los intereses solo guardan propiedad_id, por lo que el componente cruza ese id
 * contra el catálogo de propiedades ya cargado en la aplicación.
 *
 * El formulario para asociar está oculto por defecto y se despliega con el botón
 * del encabezado, para no alargar la ficha cuando solo se quiere consultar.
 *
 * Props:
 * - intereses: lista de intereses del lead
 * - propiedades: catálogo completo de propiedades
 * - cargando / error: estado de la carga
 * - alGuardar: función que recibe { propiedad_id, nivel_interes, notas }
 * - alEliminar: función que recibe el id del interés a quitar
 */

// El nivel de interés reutiliza el mismo lenguaje visual que la prioridad
const CLASE_NIVEL = { Alto: 'alta', Medio: 'media', Bajo: 'baja' };

function PropiedadesInteres({
  intereses,
  propiedades = [],
  cargando,
  error,
  alGuardar,
  alEliminar,
}) {
  const [mostrandoForm, setMostrandoForm] = useState(false);
  const [propiedadId, setPropiedadId] = useState('');
  const [nivelInteres, setNivelInteres] = useState('Medio');
  const [notas, setNotas] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [errorForm, setErrorForm] = useState(null);
  const [quitandoId, setQuitandoId] = useState(null);

  const porId = propiedades.reduce((acc, prop) => {
    acc[prop.id] = prop;
    return acc;
  }, {});

  // Solo se ofrecen las propiedades que este lead todavía no tiene asociadas
  const disponibles = propiedades.filter(
    (prop) => !intereses.some((i) => i.propiedad_id === prop.id)
  );

  const cerrarForm = () => {
    setMostrandoForm(false);
    setPropiedadId('');
    setNivelInteres('Medio');
    setNotas('');
    setErrorForm(null);
  };

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (!propiedadId) {
      setErrorForm('Selecciona una propiedad');
      return;
    }

    try {
      setGuardando(true);
      setErrorForm(null);
      await alGuardar({
        propiedad_id: parseInt(propiedadId, 10),
        nivel_interes: nivelInteres,
        notas: notas.trim() || null,
      });
      cerrarForm();
    } catch (err) {
      setErrorForm(err.message || 'No se pudo registrar el interés');
    } finally {
      setGuardando(false);
    }
  };

  const manejarQuitar = (interes) => {
    setQuitandoId(interes.id);
    Promise.resolve(alEliminar(interes.id)).finally(() => setQuitandoId(null));
  };

  return (
    <>
      <div className="ficha-seccion-encabezado">
        <span className="ficha-seccion-titulo">
          Propiedades de interés {intereses.length > 0 && `(${intereses.length})`}
        </span>

        {!mostrandoForm && disponibles.length > 0 && (
          <button className="btn-secondary" onClick={() => setMostrandoForm(true)}>
            <Icono nombre="mas" tamano={13} />
            Asociar
          </button>
        )}
      </div>

      {mostrandoForm && (
        <form className="form-lead" onSubmit={manejarEnvio} style={{ marginBottom: '1rem' }}>
          {errorForm && (
            <div className="alert-error">
              <Icono nombre="alerta" />
              <span>{errorForm}</span>
            </div>
          )}

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="propiedad-interes">Propiedad</label>
              <select
                id="propiedad-interes"
                value={propiedadId}
                onChange={(e) => setPropiedadId(e.target.value)}
                disabled={guardando}
                autoFocus
              >
                <option value="">Selecciona una propiedad</option>
                {disponibles.map((prop) => (
                  <option key={prop.id} value={prop.id}>
                    {prop.titulo}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="nivel-interes">Nivel de interés</label>
              <select
                id="nivel-interes"
                value={nivelInteres}
                onChange={(e) => setNivelInteres(e.target.value)}
                disabled={guardando}
              >
                <option value="Alto">Alto</option>
                <option value="Medio">Medio</option>
                <option value="Bajo">Bajo</option>
              </select>
            </div>

            <div className="form-group form-group-full">
              <label htmlFor="notas-interes">Notas</label>
              <input
                id="notas-interes"
                type="text"
                placeholder="Le gustó la ubicación, consulta por financiamiento"
                value={notas}
                onChange={(e) => setNotas(e.target.value)}
                disabled={guardando}
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={cerrarForm} disabled={guardando}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={guardando}>
              {guardando ? 'Guardando...' : 'Asociar propiedad'}
            </button>
          </div>
        </form>
      )}

      {cargando ? (
        <div className="state-message">Cargando propiedades de interés...</div>
      ) : error ? (
        <div className="alert-error">
          <Icono nombre="alerta" />
          <span>{error}</span>
        </div>
      ) : intereses.length === 0 ? (
        <div className="state-message empty">
          <span className="vacio-titulo">Sin propiedades asociadas</span>
          <span className="vacio-detalle">
            {propiedades.length === 0
              ? 'Primero carga propiedades en el catálogo.'
              : 'Asocia las propiedades que este lead está evaluando.'}
          </span>
        </div>
      ) : (
        <ul className="interes-lista">
          {intereses.map((interes) => {
            const prop = porId[interes.propiedad_id];

            return (
              <li key={interes.id} className="interes-item">
                <div className="interes-info">
                  <span className="interes-titulo">
                    {prop ? prop.titulo : `Propiedad #${interes.propiedad_id}`}
                  </span>
                  {prop && (
                    <span className="interes-detalle">
                      {prop.tipo} · {prop.direccion} · {prop.precio.toLocaleString('es-CL')}
                    </span>
                  )}
                  {interes.notas && <span className="interes-notas">{interes.notas}</span>}
                </div>

                <div className="interes-acciones">
                  <span
                    className={`prioridad prioridad-${CLASE_NIVEL[interes.nivel_interes] || 'media'}`}
                  >
                    <span className="prioridad-punto" />
                    {interes.nivel_interes}
                  </span>
                  <button
                    className="btn-icono peligro"
                    onClick={() => manejarQuitar(interes)}
                    disabled={quitandoId === interes.id}
                    title="Quitar de la lista de interés"
                  >
                    <Icono nombre="cerrar" tamano={14} />
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}

export default PropiedadesInteres;

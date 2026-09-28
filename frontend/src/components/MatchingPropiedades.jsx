import React, { useState } from 'react';
import Icono from './Iconos';

const tono = {
  Excelente: 'exito',
  Buena: 'info',
  Parcial: 'alerta',
  'Sin datos': 'neutra',
};

function MatchingPropiedades({ resultados, cargando, error, intereses, alAsociar }) {
  const [abierto, setAbierto] = useState(null);
  const [guardando, setGuardando] = useState(null);
  const [errorAccion, setErrorAccion] = useState(null);

  const asociar = async (resultado) => {
    try {
      setGuardando(resultado.propiedad.id);
      setErrorAccion(null);
      await alAsociar({
        propiedad_id: resultado.propiedad.id,
        nivel_interes: resultado.puntaje >= 80 ? 'Alto' : 'Medio',
        notas: `Sugerida por matching determinista (${resultado.puntaje ?? 'sin puntaje'}%).`,
      });
    } catch (err) {
      setErrorAccion(err.message || 'No se pudo asociar la propiedad');
    } finally {
      setGuardando(null);
    }
  };

  if (cargando) return <div className="state-message">Calculando coincidencias...</div>;
  if (error) return <div className="alert-error"><Icono nombre="alerta" />{error}</div>;
  if (!resultados.length) return <p className="nota-prioridad">No hay propiedades disponibles para comparar.</p>;

  return <div className="matching-lista">
    {errorAccion && <div className="alert-error">{errorAccion}</div>}
    {resultados.map((resultado) => {
      const propiedad = resultado.propiedad;
      const asociado = intereses.some((interes) => interes.propiedad_id === propiedad.id);
      const desplegado = abierto === propiedad.id;
      return <article className="matching-card" key={propiedad.id}>
        <div className="matching-cabecera">
          <div>
            <strong>{propiedad.titulo}</strong>
            <span>{propiedad.comuna || 'Comuna sin registrar'} · {propiedad.tipo}</span>
          </div>
          <div className="matching-puntaje">
            <strong>{resultado.puntaje == null ? '—' : `${resultado.puntaje}%`}</strong>
            <span className={`etiqueta ${tono[resultado.categoria] || 'neutra'}`}>{resultado.categoria}</span>
          </div>
        </div>
        <div className="matching-meta">
          <span>{propiedad.precio.toLocaleString('es-CL')} {propiedad.moneda || ''}</span>
          <span>{propiedad.dormitorios ?? '—'} dorm. · {propiedad.banos ?? '—'} {propiedad.banos === 1 ? 'baño' : 'baños'}</span>
          <span>Cobertura de datos: {resultado.cobertura}%</span>
        </div>
        {desplegado && <div className="matching-detalle">
          <ul>
            {resultado.criterios.map((criterio) => <li className={criterio.coincide ? 'cumple' : 'no-cumple'} key={criterio.nombre}>
              <span>{criterio.coincide ? '✓' : '×'}</span><div><strong>{criterio.nombre}</strong><small>{criterio.detalle}</small></div>
            </li>)}
          </ul>
          {resultado.datos_faltantes.length > 0 && <p>Falta completar: {resultado.datos_faltantes.join(', ')}.</p>}
        </div>}
        <div className="matching-acciones">
          <button className="btn-secondary" onClick={() => setAbierto(desplegado ? null : propiedad.id)}>{desplegado ? 'Ocultar razones' : 'Ver razones'}</button>
          <button className="btn-primary" disabled={asociado || guardando === propiedad.id} onClick={() => asociar(resultado)}>{asociado ? 'Ya asociada' : guardando === propiedad.id ? 'Asociando...' : 'Marcar interés'}</button>
        </div>
      </article>;
    })}
    <p className="nota-prioridad">El porcentaje se calcula con reglas; la cobertura indica cuántos datos se pudieron comparar. No es una decisión automática ni una predicción de compra.</p>
  </div>;
}

export default MatchingPropiedades;

import React, { useState } from 'react';
import Icono from './Iconos';

export const ETAPAS_PIPELINE = ['Contacto', 'Visita', 'Oferta', 'Negociación', 'Ganada', 'Perdida'];
const ABIERTAS = new Set(['Contacto', 'Visita', 'Oferta', 'Negociación']);

const dinero = (valor, moneda) => valor == null
  ? 'Valor sin definir'
  : `${new Intl.NumberFormat('es-CL').format(valor)} ${moneda || ''}`.trim();

const fecha = (valor) => valor
  ? new Date(`${valor}T12:00:00`).toLocaleDateString('es-CL')
  : 'Sin fecha';

function Tarjeta({ oportunidad, alEditar, alEliminar, alCambiarEtapa }) {
  return (
    <article className={`pipeline-card etapa-${oportunidad.etapa.toLowerCase().replace('ó', 'o')}`}>
      <div className="pipeline-card-cabecera">
        <span className="pipeline-card-lead">{oportunidad.lead_nombre || 'Lead eliminado'}</span>
        <span className="pipeline-probabilidad">{oportunidad.probabilidad}%</span>
      </div>
      <span className="pipeline-card-propiedad">{oportunidad.propiedad_titulo || 'Sin propiedad asociada'}</span>
      <strong className="pipeline-card-valor">{dinero(oportunidad.valor_estimado, oportunidad.moneda)}</strong>
      <div className="pipeline-card-meta">
        <span>{oportunidad.tipo_operacion}</span><span>·</span><span>{fecha(oportunidad.fecha_cierre_estimada)}</span>
      </div>
      {oportunidad.motivo_cierre && <p className="pipeline-motivo">{oportunidad.motivo_cierre}</p>}
      <div className="pipeline-card-acciones">
        <select value={oportunidad.etapa} onChange={(e) => alCambiarEtapa(oportunidad, e.target.value)} aria-label={`Etapa de ${oportunidad.lead_nombre || 'oportunidad'}`}>
          {ETAPAS_PIPELINE.map((etapa) => <option key={etapa}>{etapa}</option>)}
        </select>
        <button className="btn-icono" onClick={() => alEditar(oportunidad)} title="Editar"><Icono nombre="editar" /></button>
        <button className="btn-icono peligro" onClick={() => alEliminar(oportunidad)} title="Eliminar"><Icono nombre="eliminar" /></button>
      </div>
    </article>
  );
}

function PipelineOportunidades({ oportunidades, cargando, error, alEditar, alEliminar, alCambiarEtapa }) {
  const [modo, setModo] = useState('kanban');
  const [busqueda, setBusqueda] = useState('');

  if (cargando) return <div className="state-message">Cargando pipeline...</div>;
  if (error) return <div className="panel-cuerpo"><div className="alert-error"><Icono nombre="alerta" />{error}</div></div>;

  const termino = busqueda.toLowerCase().trim();
  const filtradas = oportunidades.filter((o) => !termino || [o.lead_nombre, o.propiedad_titulo, o.ejecutivo_nombre, o.tipo_operacion].some((v) => v?.toLowerCase().includes(termino)));
  const abiertas = oportunidades.filter((o) => ABIERTAS.has(o.etapa));
  const totales = abiertas.reduce((acum, o) => {
    if (o.valor_estimado != null && o.moneda) acum[o.moneda] = (acum[o.moneda] || 0) + o.valor_estimado;
    return acum;
  }, {});
  const ponderados = abiertas.reduce((acum, o) => {
    if (o.valor_estimado != null && o.moneda) acum[o.moneda] = (acum[o.moneda] || 0) + o.valor_estimado * o.probabilidad / 100;
    return acum;
  }, {});

  return (
    <>
      <div className="pipeline-resumen">
        <div><span>Negocios abiertos</span><strong>{abiertas.length}</strong></div>
        <div><span>Valor abierto</span><strong>{Object.entries(totales).map(([m, v]) => dinero(v, m)).join(' · ') || 'Sin monto'}</strong></div>
        <div><span>Pipeline ponderado</span><strong>{Object.entries(ponderados).map(([m, v]) => dinero(Math.round(v), m)).join(' · ') || 'Sin monto'}</strong></div>
        <div><span>Cerradas ganadas</span><strong>{oportunidades.filter((o) => o.etapa === 'Ganada').length}</strong></div>
      </div>

      <div className="barra-herramientas">
        <div className="campo-busqueda"><Icono nombre="buscar" tamano={14} /><input className="search-input" type="search" placeholder="Buscar lead, propiedad o ejecutivo" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} /></div>
        <div className="selector-vista">
          <button className={modo === 'kanban' ? 'activo' : ''} onClick={() => setModo('kanban')}>Pipeline</button>
          <button className={modo === 'tabla' ? 'activo' : ''} onClick={() => setModo('tabla')}>Tabla</button>
        </div>
        <span className="results-count">{filtradas.length} de {oportunidades.length}</span>
      </div>

      {oportunidades.length === 0 ? (
        <div className="state-message empty"><Icono nombre="negocio" tamano={20} /><span className="vacio-titulo">Todavía no hay oportunidades</span><span className="vacio-detalle">Crea el primer negocio para comenzar a medir el pipeline.</span></div>
      ) : modo === 'kanban' ? (
        <div className="pipeline-kanban">
          {ETAPAS_PIPELINE.map((etapa) => {
            const items = filtradas.filter((o) => o.etapa === etapa);
            return <section className="pipeline-columna" key={etapa}>
              <div className="pipeline-columna-titulo"><span>{etapa}</span><span>{items.length}</span></div>
              <div className="pipeline-columna-lista">
                {items.map((o) => <Tarjeta key={o.id} oportunidad={o} alEditar={alEditar} alEliminar={alEliminar} alCambiarEtapa={alCambiarEtapa} />)}
                {items.length === 0 && <span className="pipeline-vacio">Sin negocios</span>}
              </div>
            </section>;
          })}
        </div>
      ) : (
        <div className="table-wrapper"><table className="leads-table"><thead><tr><th>Lead / propiedad</th><th>Etapa</th><th>Valor</th><th>Prob.</th><th>Cierre estimado</th><th>Responsable</th><th /></tr></thead><tbody>
          {filtradas.map((o) => <tr key={o.id}>
            <td><div className="celda-doble"><span className="celda-principal">{o.lead_nombre || 'Lead eliminado'}</span><span className="celda-secundaria">{o.propiedad_titulo || 'Sin propiedad'} · {o.tipo_operacion}</span></div></td>
            <td><select className="select-celda" value={o.etapa} onChange={(e) => alCambiarEtapa(o, e.target.value)}>{ETAPAS_PIPELINE.map((etapa) => <option key={etapa}>{etapa}</option>)}</select></td>
            <td className="col-numero">{dinero(o.valor_estimado, o.moneda)}</td><td>{o.probabilidad}%</td><td>{fecha(o.fecha_cierre_estimada)}</td><td>{o.ejecutivo_nombre || 'Sin asignar'}</td>
            <td className="col-acciones"><div className="acciones-celda"><button className="btn-icono" onClick={() => alEditar(o)} title="Editar"><Icono nombre="editar" /></button><button className="btn-icono peligro" onClick={() => alEliminar(o)} title="Eliminar"><Icono nombre="eliminar" /></button></div></td>
          </tr>)}
        </tbody></table></div>
      )}
    </>
  );
}

export default PipelineOportunidades;

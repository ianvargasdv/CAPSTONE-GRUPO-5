import React, { useRef, useState } from 'react';
import Icono from './Iconos';
import ListadoPaginado from './ListadoPaginado';

export const ETAPAS_PIPELINE = ['Contacto', 'Visita', 'Oferta', 'Negociación', 'Ganada', 'Perdida'];
const ABIERTAS = new Set(['Contacto', 'Visita', 'Oferta', 'Negociación']);

const dinero = (valor, moneda) => valor == null
  ? 'Valor sin definir'
  : `${new Intl.NumberFormat('es-CL').format(valor)} ${moneda || ''}`.trim();

const fecha = (valor) => valor
  ? new Date(`${valor}T12:00:00`).toLocaleDateString('es-CL')
  : 'Sin fecha';

function Tarjeta({ oportunidad, alEditar, alEliminar, alCambiarEtapa, mostrarEtapa = false }) {
  return (
    <article className={`pipeline-card etapa-${oportunidad.etapa.toLowerCase().replace('ó', 'o')}`}>
      {mostrarEtapa && <span className="etiqueta neutra pipeline-etapa-movil">{oportunidad.etapa}</span>}
      <div className="pipeline-card-cabecera">
        <span className="pipeline-card-lead">{oportunidad.lead_nombre || 'Lead eliminado'}</span>
        <span className="pipeline-probabilidad">{oportunidad.probabilidad}%</span>
      </div>
      <span className="pipeline-card-propiedad">{oportunidad.propiedad_titulo || 'Sin propiedad asociada'}</span>
      <strong className="pipeline-card-valor">{dinero(oportunidad.valor_estimado, oportunidad.moneda)}</strong>
      <details className="pipeline-detalle"><summary>Detalles y acciones</summary>
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
      </details>
    </article>
  );
}

function PipelineOportunidades({ oportunidades, cargando, error, alEditar, alEliminar, alCambiarEtapa }) {
  const [modo, setModo] = useState('kanban');
  const [busqueda, setBusqueda] = useState('');
  const [grupo, setGrupo] = useState('abiertos');
  const [etapaMovil, setEtapaMovil] = useState('todas');
  const [expandidas, setExpandidas] = useState({});
  const tablero = useRef(null);

  if (cargando) return <div className="state-message">Cargando negocios...</div>;
  if (error) return <div className="panel-cuerpo"><div className="alert-error"><Icono nombre="alerta" />{error}</div></div>;

  const termino = busqueda.toLowerCase().trim();
  const filtradas = oportunidades.filter((o) => (grupo === 'todos' || (grupo === 'abiertos' ? ABIERTAS.has(o.etapa) : !ABIERTAS.has(o.etapa))) && (!termino || [o.lead_nombre, o.propiedad_titulo, o.ejecutivo_nombre, o.tipo_operacion].some((v) => v?.toLowerCase().includes(termino))));
  const abiertas = oportunidades.filter((o) => ABIERTAS.has(o.etapa));
  const etapasVisibles = ETAPAS_PIPELINE.filter(etapa => grupo === 'todos' || (grupo === 'abiertos' ? ABIERTAS.has(etapa) : !ABIERTAS.has(etapa)));
  const filtradasMovil = filtradas.filter(o => etapaMovil === 'todas' || o.etapa === etapaMovil);
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
        <div><span>Valor de negocios abiertos</span><strong>{Object.entries(totales).map(([m, v]) => dinero(v, m)).join(' · ') || 'Sin monto'}</strong></div>
        <div title="Suma del valor de cada negocio multiplicado por su probabilidad estimada; no es un ingreso asegurado."><span>Valor según probabilidad</span><strong>{Object.entries(ponderados).map(([m, v]) => dinero(Math.round(v), m)).join(' · ') || 'Sin monto'}</strong></div>
        <div><span>Negocios concretados</span><strong>{oportunidades.filter((o) => o.etapa === 'Ganada').length}</strong></div>
      </div>

      <details className="pipeline-montos-movil">
        <summary><span className="resumen-abrir">Ver montos</span><span className="resumen-cerrar">Ocultar montos</span></summary>
        <dl>
          <div><dt>Valor de negocios abiertos</dt><dd>{Object.entries(totales).map(([m, v]) => dinero(v, m)).join(' · ') || 'Sin monto'}</dd></div>
          <div><dt>Valor según probabilidad</dt><dd>{Object.entries(ponderados).map(([m, v]) => dinero(Math.round(v), m)).join(' · ') || 'Sin monto'}</dd></div>
        </dl>
        <p>El valor según probabilidad suma cada negocio multiplicado por su probabilidad estimada.</p>
      </details>

      <div className="barra-herramientas">
        <select className="filter-select" aria-label="Mostrar negocios" value={grupo} onChange={e => { setGrupo(e.target.value); setExpandidas({}); setEtapaMovil('todas'); }}><option value="abiertos">Abiertos</option><option value="cerrados">Cerrados</option><option value="todos">Todos los negocios</option></select>
        <div className="campo-busqueda"><Icono nombre="buscar" tamano={14} /><input className="search-input" type="search" aria-label="Buscar negocios" placeholder="Buscar lead, propiedad o ejecutivo" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} /></div>
        <div className="selector-vista">
          <button className={modo === 'kanban' ? 'activo' : ''} onClick={() => setModo('kanban')}>Por etapas</button>
          <button className={modo === 'tabla' ? 'activo' : ''} onClick={() => setModo('tabla')}>Tabla</button>
        </div>
        <span className="results-count">{filtradas.length} de {oportunidades.length}</span>
      </div>

      <div className="pipeline-escritorio">
      {modo === 'kanban' && oportunidades.length > 0 && <div className="pipeline-navegacion">
        <span>Recorre las etapas o elige la vista Tabla.</span>
        <div><button className="btn-secondary" aria-label="Ver etapas anteriores" onClick={() => tablero.current?.scrollBy({left: -260, behavior: 'smooth'})}>Anterior</button>
        <button className="btn-secondary" aria-label="Ver etapas siguientes" onClick={() => tablero.current?.scrollBy({left: 260, behavior: 'smooth'})}>Siguiente</button></div>
      </div>}
      {oportunidades.length === 0 ? (
        <div className="state-message empty"><Icono nombre="negocio" tamano={20} /><span className="vacio-titulo">Todavía no hay negocios</span><span className="vacio-detalle">Crea un negocio para seguir una venta o un arriendo desde el contacto hasta el cierre.</span></div>
      ) : modo === 'kanban' ? (
        <div ref={tablero} className="pipeline-kanban" tabIndex={0} role="region" aria-label="Negocios por etapas; desplázate horizontalmente para ver todas las columnas">
          {ETAPAS_PIPELINE.filter(etapa => grupo === 'todos' || (grupo === 'abiertos' ? ABIERTAS.has(etapa) : !ABIERTAS.has(etapa))).map((etapa) => {
            const items = filtradas.filter((o) => o.etapa === etapa);
            return <section className="pipeline-columna" key={etapa}>
              <div className="pipeline-columna-titulo"><span>{etapa}</span><span>{items.length}</span></div>
              <div className="pipeline-columna-lista">
                {(expandidas[etapa] ? items : items.slice(0, 5)).map((o) => <Tarjeta key={o.id} oportunidad={o} alEditar={alEditar} alEliminar={alEliminar} alCambiarEtapa={alCambiarEtapa} />)}
                {items.length > 5 && <button className="btn-secondary" onClick={() => setExpandidas(prev => ({...prev, [etapa]: !prev[etapa]}))}>{expandidas[etapa] ? 'Mostrar menos' : `Ver ${items.length - 5} más`}</button>}
                {items.length === 0 && <span className="pipeline-vacio">Sin negocios</span>}
              </div>
            </section>;
          })}
        </div>
      ) : (
        <ListadoPaginado key={JSON.stringify([busqueda, grupo])} items={filtradas} etiqueta="negocios">{(visibles) => (<div className="table-wrapper"><table className="leads-table"><thead><tr><th>Lead / propiedad</th><th>Etapa</th><th>Valor</th><th>Prob.</th><th>Cierre estimado</th><th>Responsable</th><th /></tr></thead><tbody>
          {visibles.map((o) => <tr key={o.id}>
            <td><div className="celda-doble"><span className="celda-principal">{o.lead_nombre || 'Lead eliminado'}</span><span className="celda-secundaria">{o.propiedad_titulo || 'Sin propiedad'} · {o.tipo_operacion}</span></div></td>
            <td><select className="select-celda" value={o.etapa} onChange={(e) => alCambiarEtapa(o, e.target.value)}>{ETAPAS_PIPELINE.map((etapa) => <option key={etapa}>{etapa}</option>)}</select></td>
            <td className="col-numero">{dinero(o.valor_estimado, o.moneda)}</td><td>{o.probabilidad}%</td><td>{fecha(o.fecha_cierre_estimada)}</td><td>{o.ejecutivo_nombre || 'Sin asignar'}</td>
            <td className="col-acciones"><div className="acciones-celda"><button className="btn-icono" onClick={() => alEditar(o)} title="Editar"><Icono nombre="editar" /></button><button className="btn-icono peligro" onClick={() => alEliminar(o)} title="Eliminar"><Icono nombre="eliminar" /></button></div></td>
          </tr>)}
        </tbody></table></div>)}</ListadoPaginado>
      )}
      </div>

      <section className="negocios-movil" aria-label="Lista de negocios">
        <div className="negocios-movil-filtro">
          <label htmlFor="negocios-etapa">Etapa</label>
          <select id="negocios-etapa" value={etapaMovil} onChange={e => setEtapaMovil(e.target.value)}>
            <option value="todas">Todas las etapas</option>
            {etapasVisibles.map(etapa => <option key={etapa} value={etapa}>{etapa} ({filtradas.filter(o => o.etapa === etapa).length})</option>)}
          </select>
          <span role="status">{filtradasMovil.length} de {oportunidades.length} negocios</span>
        </div>
        {filtradasMovil.length === 0 ? <div className="state-message empty">
          <span className="vacio-titulo">{oportunidades.length ? 'Sin resultados' : 'Todavía no hay negocios'}</span>
          <span className="vacio-detalle">{oportunidades.length ? 'Ajusta la búsqueda, el estado o la etapa.' : 'Crea un negocio para iniciar el seguimiento.'}</span>
        </div> : <ListadoPaginado key={JSON.stringify([busqueda, grupo, etapaMovil])} items={filtradasMovil} etiqueta="negocios">
          {visibles => <div className="negocios-movil-lista">{visibles.map(o =>
            <Tarjeta key={o.id} oportunidad={o} mostrarEtapa alEditar={alEditar} alEliminar={alEliminar} alCambiarEtapa={alCambiarEtapa} />)}
          </div>}
        </ListadoPaginado>}
      </section>
    </>
  );
}

export default PipelineOportunidades;

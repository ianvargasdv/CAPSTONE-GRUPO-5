import React, { useEffect, useState } from 'react';
import Icono from './Iconos';
import ListadoPaginado from './ListadoPaginado';
import { obtenerEjecutivos, obtenerLeads } from '../api';
import { filtrarClientes, parametrosCartera } from '../cartera';

/**
 * Listado de leads. Es la vista principal de la sección: la creación y edición
 * ocurren en un panel lateral, no en un formulario sobre la tabla.
 *
 * Los leads llegan ordenados por prioridad calculada desde el backend, así que la
 * primera fila es la que hay que atender primero. La columna Atención resume ese
 * cálculo y el detalle de por qué está en la ficha del lead.
 *
 * Props:
 * - leads: lista de leads, con los campos de prioridad ya calculados
 * - tareas: lista de tareas, para contar las abiertas de cada lead
 * - cargando / error: estado de la carga
 * - alVerFicha: abre la ficha completa del lead
 * - alEditar: abre el panel de edición
 * - alPedirEliminar: solicita la eliminación (la confirmación la maneja App)
 * - alCambiarEstado: recibe (lead, nuevoEstado) para el cambio rápido
 */

const ESTADOS = ['Nuevo', 'Contactado', 'Calificado', 'Cerrado'];

const CATEGORIAS = ['Urgente', 'Alta', 'Normal', 'Baja', 'Sin acción'];

// Solo las categorías que exigen acción llevan color
const TONO_CATEGORIA = {
  Urgente: 'peligro',
  Alta: 'alerta',
  Normal: 'neutra',
  Baja: 'neutra',
  'Sin acción': 'neutra',
};

const DIAS_SIN_CONTACTO_CRITICO = 14;

function TablaLeads({
  leads,
  tareas = [],
  cargando,
  error,
  usuario,
  alActualizar,
  alVerFicha,
  alEditar,
  alPedirEliminar,
  alCambiarEstado,
}) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroCategoria, setFiltroCategoria] = useState('Todas');
  const [cartera, setCartera] = useState('todos');
  const [resultadoCartera, setResultadoCartera] = useState(null);
  const [responsables, setResponsables] = useState([]);
  const [errorResponsables, setErrorResponsables] = useState('');
  const [version, setVersion] = useState(0);

  useEffect(() => {
    if (usuario?.rol !== 'admin') return undefined;
    let vigente = true;
    setErrorResponsables('');
    obtenerEjecutivos()
      .then((datos) => { if (vigente) setResponsables(datos); })
      .catch((e) => { if (vigente) setErrorResponsables(e.message); });
    return () => { vigente = false; };
  }, [usuario?.id, usuario?.rol, version]);

  useEffect(() => {
    if (cartera === 'todos') return undefined;
    let vigente = true;
    const guardar = (items, mensaje = '') => {
      if (vigente) setResultadoCartera({ cartera, base: leads, version, items, error: mensaje });
    };
    try {
      obtenerLeads(parametrosCartera(cartera, usuario))
        .then((items) => guardar(items))
        .catch((e) => guardar([], e.message));
    } catch (e) { guardar([], e.message); }
    return () => { vigente = false; };
  }, [cartera, leads, version, usuario?.id, usuario?.rol]);

  // Ocultar resultados de otra consulta también durante cambios rápidos o reasignaciones.
  const resultadoVigente = resultadoCartera?.cartera === cartera
    && resultadoCartera?.base === leads && resultadoCartera?.version === version;
  const cargandoCartera = cartera !== 'todos' && !resultadoVigente;
  const errorCartera = cartera !== 'todos' && resultadoVigente ? resultadoCartera.error : '';
  const clientesCartera = cartera === 'todos' ? (leads || []) : resultadoVigente ? resultadoCartera.items : [];
  const leadsFiltrados = filtrarClientes(clientesCartera, busqueda, filtroEstado, filtroCategoria);
  const nombreCartera = cartera === 'todos' ? 'Todos' : cartera === 'mia' ? 'Mi cartera'
    : cartera === 'sin_asignar' ? 'Sin asignar'
      : responsables.find((u) => `responsable:${u.id}` === cartera)?.nombre || 'Responsable seleccionado';

  const actualizar = () => {
    setVersion((v) => v + 1);
    if (cartera === 'todos') alActualizar?.();
  };

  if (cargando) {
    return <div className="state-message">Cargando leads...</div>;
  }

  if (error) {
    return (
      <div className="panel-cuerpo">
        <div className="alert-error">
          <Icono nombre="alerta" />
          <span>{error}</span>
        </div>
        <button type="button" className="btn-secondary" onClick={alActualizar}>Reintentar</button>
      </div>
    );
  }

  const tareasAbiertas = (leadId) =>
    tareas.filter((t) => t.lead_id === leadId && t.estado !== 'Completada').length;

  return (
    <>
      <div className="barra-cartera">
        <label htmlFor="cartera-clientes">Cartera</label>
        <select id="cartera-clientes" className="filter-select" value={cartera}
          onChange={(e) => setCartera(e.target.value)}>
          <option value="todos">Todos los clientes</option>
          <option value="mia">Mi cartera</option>
          {usuario?.rol === 'admin' && <>
            <option value="sin_asignar">Sin asignar</option>
            <optgroup label="Responsables activos">
              {responsables.map((u) => <option key={u.id} value={`responsable:${u.id}`}>{u.nombre}{u.rol === 'admin' ? ' (administración)' : ''}</option>)}
            </optgroup>
            {cartera.startsWith('responsable:') && !responsables.some((u) => `responsable:${u.id}` === cartera) &&
              <option value={cartera} disabled>Responsable no disponible</option>}
          </>}
        </select>
        <button type="button" className="btn-secondary" onClick={actualizar} disabled={cargandoCartera}>Actualizar cartera</button>
        {errorResponsables && <span className="cartera-aviso" role="alert">{errorResponsables}. Usa Actualizar cartera para reintentar.</span>}
      </div>
      <div className="barra-herramientas">
        <div className="campo-busqueda">
          <Icono nombre="buscar" tamano={14} />
          <input
            type="search"
            className="search-input"
            placeholder="Nombre, correo, comuna o responsable"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            aria-label="Buscar leads"
          />
        </div>

        <select
          className="filter-select"
          value={filtroCategoria}
          onChange={(e) => setFiltroCategoria(e.target.value)}
          aria-label="Filtrar por nivel de atención"
        >
          <option value="Todas">Toda la atención</option>
          {CATEGORIAS.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={filtroEstado}
          onChange={(e) => setFiltroEstado(e.target.value)}
          aria-label="Filtrar por estado"
        >
          <option value="Todos">Todos los estados</option>
          {ESTADOS.map((estado) => (
            <option key={estado} value={estado}>
              {estado}
            </option>
          ))}
        </select>

        {(busqueda || filtroEstado !== 'Todos' || filtroCategoria !== 'Todas') &&
          <button className="btn-secondary" onClick={() => {setBusqueda('');setFiltroEstado('Todos');setFiltroCategoria('Todas');}}>Limpiar filtros</button>}
        <span className="results-count" role="status">
          {cargandoCartera ? 'Consultando cartera…' : errorCartera ? 'Cartera sin cargar' : `${leadsFiltrados.length} de ${clientesCartera.length} · ${nombreCartera}`}
        </span>
      </div>

      {cargandoCartera ? <div className="state-message" role="status">Cargando cartera…</div> : errorCartera ? (
        <div className="panel-cuerpo"><div className="alert-error" role="alert">{errorCartera}</div>
          <button type="button" className="btn-secondary" onClick={actualizar}>Reintentar consulta</button></div>
      ) : leadsFiltrados.length === 0 ? (
        <div className="state-message empty">
          <span className="vacio-titulo">{clientesCartera.length ? 'Sin resultados' : cartera === 'mia' ? 'No tienes clientes asignados' : cartera === 'todos' ? 'Todavía no hay leads' : 'No hay clientes en esta cartera'}</span>
          <span className="vacio-detalle">{clientesCartera.length ? 'Ajusta la búsqueda o los filtros aplicados.' : cartera === 'todos' ? 'Registra el primer prospecto para empezar a seguir su historial de contacto.' : 'Puedes cambiar de cartera o actualizar la consulta.'}</span>
        </div>
      ) : (
        <ListadoPaginado key={JSON.stringify([busqueda,filtroEstado,filtroCategoria,cartera])} items={leadsFiltrados} etiqueta="leads">{(visibles) => ( <div className="table-wrapper" tabIndex={0} role="region" aria-label="Lista de leads; desplazamiento horizontal disponible">
          <table className="leads-table">
            <thead>
              <tr>
                <th>Lead</th>
                <th>Atención</th>
                <th>Sin contacto</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Tareas</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {visibles.map((lead) => {
                const abiertas = tareasAbiertas(lead.id);
                const nuncaContactado = lead.total_interacciones === 0;
                const critico = lead.dias_sin_contacto > DIAS_SIN_CONTACTO_CRITICO;

                return (
                  <tr key={lead.id}>
                    <td>
                      <div className="celda-doble">
                        <button className="enlace-fila" onClick={() => alVerFicha(lead)}>
                          {lead.nombre}
                        </button>
                        <span className="celda-secundaria">Responsable: {lead.ejecutivo_nombre || 'Sin asignar'}</span>
                        <details className="lead-datos-secundarios"><summary>Datos de contacto y búsqueda</summary>
                        <span className="celda-secundaria">{lead.email}</span>
                        {lead.tipo_operacion && (
                          <span className="celda-secundaria">
                            {lead.tipo_operacion} · {lead.tipo_propiedad_buscada || 'Propiedad sin definir'}
                          </span>
                        )}
                        </details>
                      </div>
                    </td>

                    <td>
                      {lead.categoria ? (
                        <span
                          className={`etiqueta ${TONO_CATEGORIA[lead.categoria] || 'neutra'}`}
                          title={`Puntaje ${lead.puntaje}. Abre la ficha para ver el detalle.`}
                        >
                          {lead.categoria}
                        </span>
                      ) : (
                        <span className="celda-vacia">—</span>
                      )}
                    </td>

                    <td>
                      {nuncaContactado ? (
                        <span className="dato-alerta">Nunca</span>
                      ) : (
                        <span className={critico ? 'dato-critico' : undefined}>
                          {lead.dias_sin_contacto} d
                        </span>
                      )}
                    </td>

                    <td>
                      {/* Cambio rápido de estado sin abrir el formulario completo */}
                      <select
                        className="select-celda"
                        value={lead.estado || 'Nuevo'}
                        onChange={(e) => alCambiarEstado(lead, e.target.value)}
                        title="Cambiar estado"
                        aria-label={`Estado de ${lead.nombre}`}
                      >
                        {ESTADOS.map((estado) => (
                          <option key={estado} value={estado}>
                            {estado}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td>
                      <span className={`prioridad prioridad-${(lead.prioridad || 'media').toLowerCase()}`}>
                        <span className="prioridad-punto" />
                        {lead.prioridad}
                      </span>
                    </td>

                    <td>
                      {abiertas > 0 ? (
                        <span className="etiqueta neutra">
                          <Icono nombre="tareas" tamano={11} />
                          {abiertas}
                        </span>
                      ) : (
                        <span className="celda-vacia">—</span>
                      )}
                    </td>

                    <td className="col-acciones">
                      <div className="acciones-celda">
                        <button
                          className="btn-secondary"
                          onClick={() => alVerFicha(lead)}
                          title="Ver ficha"
                        >
                          Ver ficha
                        </button>
                        <button className="btn-icono" onClick={() => alEditar(lead)} title="Editar">
                          <Icono nombre="editar" />
                        </button>
                        <button
                          className="btn-icono peligro"
                          onClick={() => alPedirEliminar(lead)}
                          title="Eliminar"
                        >
                          <Icono nombre="eliminar" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div> )}</ListadoPaginado>
      )}
    </>
  );
}

export default TablaLeads;

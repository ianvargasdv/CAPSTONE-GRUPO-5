import React, { useState } from 'react';

/**
 * Tabla de tareas con filtros por estado y prioridad, búsqueda por título,
 * indicador de vencimiento, y acciones de completar/editar/eliminar por fila.
 *
 * Props:
 * - tareas: lista de tareas a mostrar
 * - leads: lista de leads para mostrar el nombre asociado
 * - cargando: boolean de estado de carga
 * - error: mensaje de error si la carga falló
 * - alEditar: función que recibe el objeto tarea
 * - alEliminar: función que recibe el id de la tarea
 * - alCompletar: función que recibe el objeto tarea para marcarla como completada
 */
function TablaTareas({ tareas, leads = [], cargando, error, alEditar, alEliminar, alCompletar }) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroPrioridad, setFiltroPrioridad] = useState('Todas');
  const [eliminandoId, setEliminandoId] = useState(null);
  const [completandoId, setCompletandoId] = useState(null);

  // Mapa de id → nombre de lead para mostrar en la tabla
  const mapaLeads = leads.reduce((acc, lead) => {
    acc[lead.id] = lead.nombre;
    return acc;
  }, {});

  if (cargando) {
    return <div className="state-message">Cargando tareas...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!tareas || tareas.length === 0) {
    return (
      <div className="state-message empty">
        No hay tareas registradas aún.
      </div>
    );
  }

  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);

  /**
   * Determina si una tarea está vencida:
   * tiene fecha límite, esa fecha ya pasó, y no está completada.
   */
  const estaVencida = (tarea) => {
    if (!tarea.fecha_limite || tarea.estado === 'Completada') return false;
    const limite = new Date(tarea.fecha_limite + 'T00:00:00');
    return limite < hoy;
  };

  const tareasFiltradas = tareas.filter((tarea) => {
    const termino = busqueda.toLowerCase().trim();
    const coincideBusqueda =
      !termino || tarea.titulo.toLowerCase().includes(termino);
    const coincideEstado =
      filtroEstado === 'Todos' || tarea.estado === filtroEstado;
    const coincidePrioridad =
      filtroPrioridad === 'Todas' || tarea.prioridad === filtroPrioridad;
    return coincideBusqueda && coincideEstado && coincidePrioridad;
  });

  const manejarEliminar = (tarea) => {
    const confirmado = window.confirm(
      `¿Eliminar la tarea "${tarea.titulo}"?\nEsta acción no se puede deshacer.`
    );
    if (confirmado) {
      setEliminandoId(tarea.id);
      alEliminar(tarea.id).finally(() => setEliminandoId(null));
    }
  };

  const manejarCompletar = (tarea) => {
    setCompletandoId(tarea.id);
    alCompletar(tarea).finally(() => setCompletandoId(null));
  };

  return (
    <div className="table-container">
      <div className="filter-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Buscar tarea por título..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <select
          className="filter-select"
          value={filtroEstado}
          onChange={(e) => setFiltroEstado(e.target.value)}
        >
          <option value="Todos">Todos los estados</option>
          <option value="Pendiente">Pendiente</option>
          <option value="En Progreso">En Progreso</option>
          <option value="Completada">Completada</option>
        </select>
        <select
          className="filter-select"
          value={filtroPrioridad}
          onChange={(e) => setFiltroPrioridad(e.target.value)}
        >
          <option value="Todas">Todas las prioridades</option>
          <option value="Alta">Alta</option>
          <option value="Media">Media</option>
          <option value="Baja">Baja</option>
        </select>
        <span className="results-count">
          {tareasFiltradas.length} de {tareas.length} tareas
        </span>
      </div>

      {tareasFiltradas.length === 0 ? (
        <div className="state-message empty">
          No se encontraron tareas con los filtros aplicados.
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="leads-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Fecha límite</th>
                <th>Lead asociado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tareasFiltradas.map((tarea) => (
                <tr
                  key={tarea.id}
                  className={tarea.estado === 'Completada' ? 'fila-completada' : ''}
                >
                  <td>#{tarea.id}</td>
                  <td className="col-nombre">
                    {tarea.titulo}
                    {tarea.descripcion && (
                      <span className="tarea-descripcion">{tarea.descripcion}</span>
                    )}
                  </td>
                  <td>
                    <span className={`badge-estado-tarea estado-${tarea.estado.toLowerCase().replace(' ', '-')}`}>
                      {tarea.estado}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`badge-priority priority-${tarea.prioridad.toLowerCase()}`}
                    >
                      {tarea.prioridad}
                    </span>
                  </td>
                  <td>
                    {tarea.fecha_limite ? (
                      <span className={estaVencida(tarea) ? 'fecha-vencida' : ''}>
                        {estaVencida(tarea) && <span className="badge-vencida">Vencida</span>}
                        {new Date(tarea.fecha_limite + 'T00:00:00').toLocaleDateString('es-CL')}
                      </span>
                    ) : (
                      <span className="col-fecha">—</span>
                    )}
                  </td>
                  <td>
                    {tarea.lead_id && mapaLeads[tarea.lead_id] ? (
                      <span className="tarea-lead-badge">{mapaLeads[tarea.lead_id]}</span>
                    ) : (
                      <span className="col-fecha">—</span>
                    )}
                  </td>
                  <td>
                    <div className="acciones-celda">
                      {tarea.estado !== 'Completada' && (
                        <button
                          className="btn-accion btn-completar"
                          onClick={() => manejarCompletar(tarea)}
                          disabled={completandoId === tarea.id}
                          title="Marcar como completada"
                        >
                          {completandoId === tarea.id ? '...' : '✓'}
                        </button>
                      )}
                      <button
                        className="btn-accion btn-editar"
                        onClick={() => alEditar(tarea)}
                        title="Editar tarea"
                      >
                        Editar
                      </button>
                      <button
                        className="btn-accion btn-eliminar"
                        onClick={() => manejarEliminar(tarea)}
                        disabled={eliminandoId === tarea.id}
                        title="Eliminar tarea"
                      >
                        {eliminandoId === tarea.id ? '...' : 'Eliminar'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default TablaTareas;

import React, { useState } from 'react';

/**
 * Tabla de leads con búsqueda en tiempo real y acciones de editar/eliminar/historial por fila.
 *
 * Props:
 * - leads: lista de leads a mostrar
 * - cargando: boolean que indica si los datos están cargando
 * - error: mensaje de error si la carga falló
 * - alEditar: función que recibe el objeto lead a editar
 * - alEliminar: función que recibe el id del lead a eliminar
 * - alVerHistorial: función que recibe el objeto lead para abrir su historial
 * - leadSeleccionadoId: id del lead cuyo historial está abierto actualmente (para resaltar la fila)
 */
function TablaLeads({ leads, cargando, error, alEditar, alEliminar, alVerHistorial, leadSeleccionadoId }) {
  const [busqueda, setBusqueda] = useState('');
  const [eliminandoId, setEliminandoId] = useState(null);

  if (cargando) {
    return <div className="state-message">Cargando lista de leads...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!leads || leads.length === 0) {
    return (
      <div className="state-message empty">
        No hay leads registrados aún en Supabase.
      </div>
    );
  }

  const leadsFiltrados = leads.filter((lead) => {
    const termino = busqueda.toLowerCase().trim();
    if (!termino) return true;
    return (
      lead.nombre.toLowerCase().includes(termino) ||
      lead.email.toLowerCase().includes(termino) ||
      (lead.telefono && lead.telefono.includes(termino))
    );
  });

  const manejarEliminar = (lead) => {
    // Pide confirmación antes de eliminar
    const confirmado = window.confirm(
      `¿Eliminar el lead "${lead.nombre}"?\nEsta acción no se puede deshacer.`
    );
    if (confirmado) {
      setEliminandoId(lead.id);
      alEliminar(lead.id).finally(() => setEliminandoId(null));
    }
  };

  return (
    <div className="table-container">
      <div className="filter-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Buscar lead por nombre, email o teléfono..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <span className="results-count">
          Mostrando {leadsFiltrados.length} de {leads.length} leads
        </span>
      </div>

      {leadsFiltrados.length === 0 ? (
        <div className="state-message empty">
          No se encontraron leads que coincidan con "{busqueda}".
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="leads-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Teléfono</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {leadsFiltrados.map((lead) => (
                <tr
                  key={lead.id}
                  className={leadSeleccionadoId === lead.id ? 'fila-seleccionada' : ''}
                >
                  <td>#{lead.id}</td>
                  <td className="col-nombre">{lead.nombre}</td>
                  <td>{lead.email}</td>
                  <td>{lead.telefono || '-'}</td>
                  <td>
                    <span className="badge-status">{lead.estado}</span>
                  </td>
                  <td>
                    <span
                      className={`badge-priority priority-${
                        lead.prioridad ? lead.prioridad.toLowerCase() : 'media'
                      }`}
                    >
                      {lead.prioridad}
                    </span>
                  </td>
                  <td className="col-fecha">
                    {lead.fecha_creacion
                      ? new Date(lead.fecha_creacion).toLocaleDateString('es-CL')
                      : '-'}
                  </td>
                  <td>
                    <div className="acciones-celda">
                      <button
                        className={`btn-accion btn-historial ${leadSeleccionadoId === lead.id ? 'active' : ''}`}
                        onClick={() => alVerHistorial(lead)}
                        title="Ver historial de interacciones"
                      >
                        Historial
                      </button>
                      <button
                        className="btn-accion btn-editar"
                        onClick={() => alEditar(lead)}
                        title="Editar lead"
                      >
                        Editar
                      </button>
                      <button
                        className="btn-accion btn-eliminar"
                        onClick={() => manejarEliminar(lead)}
                        disabled={eliminandoId === lead.id}
                        title="Eliminar lead"
                      >
                        {eliminandoId === lead.id ? '...' : 'Eliminar'}
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

export default TablaLeads;

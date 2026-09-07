import React from 'react';

function TablaLeads({ leads, cargando, error }) {
  if (cargando) {
    return <div className="state-message">Cargando lista de leads...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!leads || leads.length === 0) {
    return (
      <div className="state-message empty">
        No hay leads registrados aún en la base de datos.
      </div>
    );
  }

  return (
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
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>#{lead.id}</td>
              <td className="col-nombre">{lead.nombre}</td>
              <td>{lead.email}</td>
              <td>{lead.telefono || '-'}</td>
              <td>
                <span className="badge-status">
                  {lead.estado}
                </span>
              </td>
              <td>
                <span className={`badge-priority priority-${lead.prioridad ? lead.prioridad.toLowerCase() : 'media'}`}>
                  {lead.prioridad}
                </span>
              </td>
              <td className="col-fecha">
                {lead.fecha_creacion
                  ? new Date(lead.fecha_creacion).toLocaleDateString('es-CL')
                  : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TablaLeads;

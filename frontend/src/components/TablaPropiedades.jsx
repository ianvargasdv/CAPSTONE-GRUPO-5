import React from 'react';

function TablaPropiedades({ propiedades, cargando, error }) {
  if (cargando) {
    return <div className="state-message">Cargando catálogo de propiedades...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!propiedades || propiedades.length === 0) {
    return (
      <div className="state-message empty">
        No hay propiedades registradas aún en el sistema.
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="leads-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Tipo</th>
            <th>Precio</th>
            <th>Dirección</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {propiedades.map((prop) => (
            <tr key={prop.id}>
              <td>#{prop.id}</td>
              <td className="col-nombre">{prop.titulo}</td>
              <td>{prop.tipo}</td>
              <td>
                <strong>{prop.precio ? prop.precio.toLocaleString('es-CL') : '0'}</strong>
              </td>
              <td>{prop.direccion}</td>
              <td>
                <span className={`badge-priority priority-${prop.estado ? prop.estado.toLowerCase() : 'disponible'}`}>
                  {prop.estado}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TablaPropiedades;

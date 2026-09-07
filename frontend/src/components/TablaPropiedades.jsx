import React, { useState } from 'react';

/**
 * Tabla de propiedades con búsqueda, filtro por tipo y acciones de editar/eliminar.
 *
 * Props:
 * - propiedades: lista de propiedades a mostrar
 * - cargando: boolean que indica si los datos están cargando
 * - error: mensaje de error si la carga falló
 * - alEditar: función que recibe el objeto propiedad a editar
 * - alEliminar: función que recibe el id de la propiedad a eliminar
 */
function TablaPropiedades({ propiedades, cargando, error, alEditar, alEliminar }) {
  const [busqueda, setBusqueda] = useState('');
  const [tipoFiltro, setTipoFiltro] = useState('Todos');
  const [eliminandoId, setEliminandoId] = useState(null);

  if (cargando) {
    return <div className="state-message">Cargando catálogo de propiedades...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!propiedades || propiedades.length === 0) {
    return (
      <div className="state-message empty">
        No hay propiedades registradas aún en Supabase.
      </div>
    );
  }

  const propiedadesFiltradas = propiedades.filter((prop) => {
    const termino = busqueda.toLowerCase().trim();
    const coincideBusqueda =
      !termino ||
      prop.titulo.toLowerCase().includes(termino) ||
      prop.direccion.toLowerCase().includes(termino);

    const coincideTipo =
      tipoFiltro === 'Todos' || prop.tipo.toLowerCase() === tipoFiltro.toLowerCase();

    return coincideBusqueda && coincideTipo;
  });

  const manejarEliminar = (prop) => {
    // Pide confirmación antes de eliminar
    const confirmado = window.confirm(
      `¿Eliminar la propiedad "${prop.titulo}"?\nEsta acción no se puede deshacer.`
    );
    if (confirmado) {
      setEliminandoId(prop.id);
      alEliminar(prop.id).finally(() => setEliminandoId(null));
    }
  };

  return (
    <div className="table-container">
      <div className="filter-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Buscar propiedad por título o dirección..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />

        <select
          className="filter-select"
          value={tipoFiltro}
          onChange={(e) => setTipoFiltro(e.target.value)}
        >
          <option value="Todos">Todos los tipos</option>
          <option value="Departamento">Departamento</option>
          <option value="Casa">Casa</option>
          <option value="Terreno">Terreno</option>
          <option value="Oficina">Oficina</option>
        </select>

        <span className="results-count">
          Mostrando {propiedadesFiltradas.length} de {propiedades.length} propiedades
        </span>
      </div>

      {propiedadesFiltradas.length === 0 ? (
        <div className="state-message empty">
          No se encontraron propiedades que coincidan con los filtros aplicados.
        </div>
      ) : (
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
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {propiedadesFiltradas.map((prop) => (
                <tr key={prop.id}>
                  <td>#{prop.id}</td>
                  <td className="col-nombre">{prop.titulo}</td>
                  <td>{prop.tipo}</td>
                  <td>
                    <strong>
                      {prop.precio
                        ? `$${prop.precio.toLocaleString('es-CL')}`
                        : '$0'}
                    </strong>
                  </td>
                  <td>{prop.direccion}</td>
                  <td>
                    <span
                      className={`badge-priority priority-${
                        prop.estado ? prop.estado.toLowerCase() : 'disponible'
                      }`}
                    >
                      {prop.estado}
                    </span>
                  </td>
                  <td>
                    <div className="acciones-celda">
                      <button
                        className="btn-accion btn-editar"
                        onClick={() => alEditar(prop)}
                        title="Editar propiedad"
                      >
                        Editar
                      </button>
                      <button
                        className="btn-accion btn-eliminar"
                        onClick={() => manejarEliminar(prop)}
                        disabled={eliminandoId === prop.id}
                        title="Eliminar propiedad"
                      >
                        {eliminandoId === prop.id ? '...' : 'Eliminar'}
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

export default TablaPropiedades;

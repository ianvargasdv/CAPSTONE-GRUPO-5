import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Listado del catálogo de propiedades con búsqueda y filtros por tipo y estado.
 *
 * Props:
 * - propiedades: lista de propiedades
 * - cargando / error: estado de la carga
 * - alEditar: abre el panel de edición
 * - alPedirEliminar: solicita la eliminación (la confirmación la maneja App)
 */

const TIPOS = ['Departamento', 'Casa', 'Terreno', 'Oficina'];

// Tono de la etiqueta según disponibilidad comercial
const TONO_ESTADO = {
  Disponible: 'exito',
  Reservada: 'alerta',
  Vendida: 'neutra',
};

const ICONO_TIPO = {
  Departamento: 'edificio',
  Casa: 'casa',
  Terreno: 'etiqueta',
  Oficina: 'edificio',
};

function TablaPropiedades({ propiedades, cargando, error, alEditar, alPedirEliminar }) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('Todos');
  const [filtroEstado, setFiltroEstado] = useState('Todos');

  if (cargando) {
    return <div className="state-message">Cargando catálogo...</div>;
  }

  if (error) {
    return (
      <div className="panel-cuerpo">
        <div className="alert-error">
          <Icono nombre="alerta" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  if (!propiedades || propiedades.length === 0) {
    return (
      <div className="state-message empty">
        <Icono nombre="edificio" tamano={20} />
        <span className="vacio-titulo">El catálogo está vacío</span>
        <span className="vacio-detalle">
          Carga las propiedades disponibles para poder asociarlas a los leads interesados.
        </span>
      </div>
    );
  }

  const filtradas = propiedades.filter((prop) => {
    const termino = busqueda.toLowerCase().trim();
    const coincideTexto =
      !termino ||
      prop.titulo.toLowerCase().includes(termino) ||
      prop.direccion.toLowerCase().includes(termino);
    const coincideTipo = filtroTipo === 'Todos' || prop.tipo === filtroTipo;
    const coincideEstado = filtroEstado === 'Todos' || prop.estado === filtroEstado;
    return coincideTexto && coincideTipo && coincideEstado;
  });

  return (
    <>
      <div className="barra-herramientas">
        <div className="campo-busqueda">
          <Icono nombre="buscar" tamano={14} />
          <input
            type="search"
            className="search-input"
            placeholder="Buscar por título o dirección"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            aria-label="Buscar propiedades"
          />
        </div>

        <select
          className="filter-select"
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
        >
          <option value="Todos">Todos los tipos</option>
          {TIPOS.map((tipo) => (
            <option key={tipo} value={tipo}>
              {tipo}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={filtroEstado}
          onChange={(e) => setFiltroEstado(e.target.value)}
        >
          <option value="Todos">Todos los estados</option>
          <option value="Disponible">Disponible</option>
          <option value="Reservada">Reservada</option>
          <option value="Vendida">Vendida</option>
        </select>

        <span className="results-count">
          {filtradas.length} de {propiedades.length}
        </span>
      </div>

      {filtradas.length === 0 ? (
        <div className="state-message empty">
          <span className="vacio-titulo">Sin resultados</span>
          <span className="vacio-detalle">Ajusta la búsqueda o los filtros aplicados.</span>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="leads-table">
            <thead>
              <tr>
                <th>Propiedad</th>
                <th>Tipo</th>
                <th>Precio</th>
                <th>Estado</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtradas.map((prop) => (
                <tr key={prop.id}>
                  <td>
                    <div className="celda-doble">
                      <span className="celda-principal">{prop.titulo}</span>
                      <span className="celda-secundaria">{prop.direccion}</span>
                    </div>
                  </td>

                  <td>
                    <span className="etiqueta neutra">
                      <Icono nombre={ICONO_TIPO[prop.tipo] || 'edificio'} tamano={11} />
                      {prop.tipo}
                    </span>
                  </td>

                  <td className="col-numero">
                    {prop.precio ? prop.precio.toLocaleString('es-CL') : '—'}
                  </td>

                  <td>
                    <span className={`etiqueta ${TONO_ESTADO[prop.estado] || 'neutra'}`}>
                      {prop.estado}
                    </span>
                  </td>

                  <td className="col-acciones">
                    <div className="acciones-celda">
                      <button className="btn-icono" onClick={() => alEditar(prop)} title="Editar">
                        <Icono nombre="editar" />
                      </button>
                      <button
                        className="btn-icono peligro"
                        onClick={() => alPedirEliminar(prop)}
                        title="Eliminar"
                      >
                        <Icono nombre="eliminar" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default TablaPropiedades;

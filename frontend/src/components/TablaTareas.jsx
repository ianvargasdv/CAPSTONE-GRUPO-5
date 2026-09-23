import React, { useState } from 'react';
import Icono from './Iconos';

/**
 * Listado de tareas con filtros por estado y prioridad.
 *
 * Marca visualmente las tareas vencidas, que es la información que el ejecutivo
 * necesita ver primero al revisar su carga de trabajo.
 *
 * Props:
 * - tareas: lista de tareas
 * - leads: lista de leads para resolver el nombre del lead asociado
 * - cargando / error: estado de la carga
 * - alEditar: abre el panel de edición
 * - alPedirEliminar: solicita la eliminación (la confirmación la maneja App)
 * - alCompletar: marca la tarea como completada
 */

const TONO_ESTADO = {
  Pendiente: 'alerta',
  'En Progreso': 'info',
  Completada: 'exito',
};

function TablaTareas({
  tareas,
  leads = [],
  cargando,
  error,
  alEditar,
  alPedirEliminar,
  alCompletar,
}) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroPrioridad, setFiltroPrioridad] = useState('Todas');
  const [completandoId, setCompletandoId] = useState(null);

  const nombrePorLead = leads.reduce((acc, lead) => {
    acc[lead.id] = lead.nombre;
    return acc;
  }, {});

  if (cargando) {
    return <div className="state-message">Cargando tareas...</div>;
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

  if (!tareas || tareas.length === 0) {
    return (
      <div className="state-message empty">
        <Icono nombre="tareas" tamano={20} />
        <span className="vacio-titulo">No hay tareas registradas</span>
        <span className="vacio-detalle">
          Crea tareas para organizar los seguimientos pendientes con cada lead.
        </span>
      </div>
    );
  }

  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);

  /** Una tarea está vencida si tiene fecha límite pasada y no está completada. */
  const estaVencida = (tarea) => {
    if (!tarea.fecha_limite || tarea.estado === 'Completada') return false;
    return new Date(tarea.fecha_limite + 'T00:00:00') < hoy;
  };

  const filtradas = tareas.filter((tarea) => {
    const termino = busqueda.toLowerCase().trim();
    const coincideTexto = !termino || tarea.titulo.toLowerCase().includes(termino);
    const coincideEstado = filtroEstado === 'Todos' || tarea.estado === filtroEstado;
    const coincidePrioridad = filtroPrioridad === 'Todas' || tarea.prioridad === filtroPrioridad;
    return coincideTexto && coincideEstado && coincidePrioridad;
  });

  const manejarCompletar = (tarea) => {
    setCompletandoId(tarea.id);
    Promise.resolve(alCompletar(tarea)).finally(() => setCompletandoId(null));
  };

  return (
    <>
      <div className="barra-herramientas">
        <div className="campo-busqueda">
          <Icono nombre="buscar" tamano={14} />
          <input
            type="search"
            className="search-input"
            placeholder="Buscar tarea"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            aria-label="Buscar tareas"
          />
        </div>

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
          {filtradas.length} de {tareas.length}
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
                <th>Tarea</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Vence</th>
                <th>Lead</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtradas.map((tarea) => {
                const vencida = estaVencida(tarea);
                const completada = tarea.estado === 'Completada';

                return (
                  <tr key={tarea.id}>
                    <td>
                      <div className="celda-doble">
                        <span
                          className="celda-principal"
                          style={completada ? { textDecoration: 'line-through', opacity: 0.6 } : undefined}
                        >
                          {tarea.titulo}
                        </span>
                        {tarea.descripcion && (
                          <span className="celda-secundaria">{tarea.descripcion}</span>
                        )}
                      </div>
                    </td>

                    <td>
                      <span className={`etiqueta ${TONO_ESTADO[tarea.estado] || 'neutra'}`}>
                        {tarea.estado}
                      </span>
                    </td>

                    <td>
                      <span className={`prioridad prioridad-${(tarea.prioridad || 'media').toLowerCase()}`}>
                        <span className="prioridad-punto" />
                        {tarea.prioridad}
                      </span>
                    </td>

                    <td className="col-fecha">
                      {tarea.fecha_limite ? (
                        vencida ? (
                          <span className="etiqueta peligro">
                            <Icono nombre="alerta" tamano={11} />
                            {new Date(tarea.fecha_limite + 'T00:00:00').toLocaleDateString('es-CL')}
                          </span>
                        ) : (
                          new Date(tarea.fecha_limite + 'T00:00:00').toLocaleDateString('es-CL')
                        )
                      ) : (
                        <span className="celda-vacia">—</span>
                      )}
                    </td>

                    <td>
                      {tarea.lead_id && nombrePorLead[tarea.lead_id] ? (
                        <span className="celda-secundaria">{nombrePorLead[tarea.lead_id]}</span>
                      ) : (
                        <span className="celda-vacia">—</span>
                      )}
                    </td>

                    <td className="col-acciones">
                      <div className="acciones-celda">
                        {!completada && (
                          <button
                            className="btn-icono exito"
                            onClick={() => manejarCompletar(tarea)}
                            disabled={completandoId === tarea.id}
                            title="Marcar como completada"
                          >
                            <Icono nombre="check" />
                          </button>
                        )}
                        <button className="btn-icono" onClick={() => alEditar(tarea)} title="Editar">
                          <Icono nombre="editar" />
                        </button>
                        <button
                          className="btn-icono peligro"
                          onClick={() => alPedirEliminar(tarea)}
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
        </div>
      )}
    </>
  );
}

export default TablaTareas;

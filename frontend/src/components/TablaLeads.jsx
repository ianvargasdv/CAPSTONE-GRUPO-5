import React, { useState } from 'react';
import Icono from './Iconos';

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
  alVerFicha,
  alEditar,
  alPedirEliminar,
  alCambiarEstado,
}) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroCategoria, setFiltroCategoria] = useState('Todas');

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
      </div>
    );
  }

  if (!leads || leads.length === 0) {
    return (
      <div className="state-message empty">
        <Icono nombre="usuarios" tamano={20} />
        <span className="vacio-titulo">Todavía no hay leads</span>
        <span className="vacio-detalle">
          Registra el primer prospecto para empezar a seguir su historial de contacto.
        </span>
      </div>
    );
  }

  const leadsFiltrados = leads.filter((lead) => {
    const termino = busqueda.toLowerCase().trim();
    const coincideTexto =
      !termino ||
      lead.nombre.toLowerCase().includes(termino) ||
      lead.email.toLowerCase().includes(termino) ||
      (lead.telefono && lead.telefono.includes(termino)) ||
      (lead.comunas_interes && lead.comunas_interes.toLowerCase().includes(termino));
    const coincideEstado = filtroEstado === 'Todos' || lead.estado === filtroEstado;
    const coincideCategoria = filtroCategoria === 'Todas' || lead.categoria === filtroCategoria;
    return coincideTexto && coincideEstado && coincideCategoria;
  });

  const tareasAbiertas = (leadId) =>
    tareas.filter((t) => t.lead_id === leadId && t.estado !== 'Completada').length;

  return (
    <>
      <div className="barra-herramientas">
        <div className="campo-busqueda">
          <Icono nombre="buscar" tamano={14} />
          <input
            type="search"
            className="search-input"
            placeholder="Buscar por nombre, correo o teléfono"
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

        <span className="results-count">
          {leadsFiltrados.length} de {leads.length}
        </span>
      </div>

      {leadsFiltrados.length === 0 ? (
        <div className="state-message empty">
          <span className="vacio-titulo">Sin resultados</span>
          <span className="vacio-detalle">Ajusta la búsqueda o los filtros aplicados.</span>
        </div>
      ) : (
        <div className="table-wrapper">
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
              {leadsFiltrados.map((lead) => {
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
                        <span className="celda-secundaria">{lead.email}</span>
                        {lead.tipo_operacion && (
                          <span className="celda-secundaria">
                            {lead.tipo_operacion} · {lead.tipo_propiedad_buscada || 'Propiedad sin definir'}
                          </span>
                        )}
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
                          className="btn-icono"
                          onClick={() => alVerFicha(lead)}
                          title="Ver ficha"
                        >
                          <Icono nombre="chevron" />
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
        </div>
      )}
    </>
  );
}

export default TablaLeads;

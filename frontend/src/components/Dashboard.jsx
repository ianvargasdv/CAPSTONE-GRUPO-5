import React from 'react';

/**
 * Vista de resumen del CRM.
 * Muestra KPIs generales, distribución por estados y listas de elementos recientes.
 * No hace llamadas al backend — trabaja con los datos ya cargados en App.jsx.
 *
 * Props:
 * - leads: lista completa de leads
 * - propiedades: lista completa de propiedades
 * - tareas: lista completa de tareas
 * - cargando: true mientras alguna entidad aún está cargando
 */
function Dashboard({ leads, propiedades, tareas, cargando }) {

  if (cargando) {
    return <div className="state-message">Cargando resumen...</div>;
  }

  // ── Cálculos de Leads ──
  const totalLeads = leads.length;
  const leadsPorEstado = {
    Nuevo: leads.filter((l) => l.estado === 'Nuevo').length,
    Contactado: leads.filter((l) => l.estado === 'Contactado').length,
    Calificado: leads.filter((l) => l.estado === 'Calificado').length,
    Cerrado: leads.filter((l) => l.estado === 'Cerrado').length,
  };
  const leadsRecientes = [...leads]
    .sort((a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion))
    .slice(0, 5);

  // ── Cálculos de Propiedades ──
  const totalPropiedades = propiedades.length;
  const propiedadesPorEstado = {
    Disponible: propiedades.filter((p) => p.estado === 'Disponible').length,
    Reservada: propiedades.filter((p) => p.estado === 'Reservada').length,
    Vendida: propiedades.filter((p) => p.estado === 'Vendida').length,
  };

  // ── Cálculos de Tareas ──
  const totalTareas = tareas.length;
  const tareasPendientes = tareas.filter((t) => t.estado === 'Pendiente').length;
  const tareasEnProgreso = tareas.filter((t) => t.estado === 'En Progreso').length;
  const tareasCompletadas = tareas.filter((t) => t.estado === 'Completada').length;

  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  const tareasVencidas = tareas.filter((t) => {
    if (!t.fecha_limite || t.estado === 'Completada') return false;
    return new Date(t.fecha_limite + 'T00:00:00') < hoy;
  }).length;

  // Tareas urgentes: alta prioridad, no completadas, ordenadas por fecha límite
  const tareasUrgentes = tareas
    .filter((t) => t.prioridad === 'Alta' && t.estado !== 'Completada')
    .sort((a, b) => {
      if (!a.fecha_limite) return 1;
      if (!b.fecha_limite) return -1;
      return new Date(a.fecha_limite) - new Date(b.fecha_limite);
    })
    .slice(0, 4);

  return (
    <div className="dashboard-contenido">

      {/* ── Fila de KPIs principales ── */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-numero">{totalLeads}</span>
          <span className="kpi-label">Leads totales</span>
          <span className="kpi-detalle">{leadsPorEstado.Nuevo} nuevos sin contactar</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-numero">{totalPropiedades}</span>
          <span className="kpi-label">Propiedades</span>
          <span className="kpi-detalle">{propiedadesPorEstado.Disponible} disponibles</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-numero">{tareasPendientes + tareasEnProgreso}</span>
          <span className="kpi-label">Tareas activas</span>
          <span className={`kpi-detalle ${tareasVencidas > 0 ? 'kpi-alerta' : ''}`}>
            {tareasVencidas > 0
              ? `${tareasVencidas} vencida${tareasVencidas !== 1 ? 's' : ''}`
              : 'Sin vencimientos'}
          </span>
        </div>

        <div className="kpi-card">
          <span className="kpi-numero">{tareasCompletadas}</span>
          <span className="kpi-label">Tareas completadas</span>
          <span className="kpi-detalle">
            {totalTareas > 0
              ? `${Math.round((tareasCompletadas / totalTareas) * 100)}% del total`
              : 'Sin tareas aún'}
          </span>
        </div>
      </div>

      {/* ── Fila de distribución por estado ── */}
      <div className="resumen-grid">

        {/* Leads por estado */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Leads por estado</h2>
            <span className="badge">{totalLeads} total</span>
          </div>
          <div className="distribucion-lista">
            {Object.entries(leadsPorEstado).map(([estado, cantidad]) => (
              <div key={estado} className="distribucion-item">
                <span className="distribucion-label">{estado}</span>
                <div className="distribucion-barra-wrapper">
                  <div
                    className="distribucion-barra"
                    style={{
                      width: totalLeads > 0 ? `${(cantidad / totalLeads) * 100}%` : '0%',
                    }}
                  />
                </div>
                <span className="distribucion-valor">{cantidad}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Propiedades por estado */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Propiedades por estado</h2>
            <span className="badge">{totalPropiedades} total</span>
          </div>
          <div className="distribucion-lista">
            {Object.entries(propiedadesPorEstado).map(([estado, cantidad]) => (
              <div key={estado} className="distribucion-item">
                <span className="distribucion-label">{estado}</span>
                <div className="distribucion-barra-wrapper">
                  <div
                    className={`distribucion-barra barra-${estado.toLowerCase()}`}
                    style={{
                      width: totalPropiedades > 0 ? `${(cantidad / totalPropiedades) * 100}%` : '0%',
                    }}
                  />
                </div>
                <span className="distribucion-valor">{cantidad}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ── Fila de listas recientes ── */}
      <div className="resumen-grid">

        {/* Leads recientes */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Últimos leads registrados</h2>
          </div>
          {leadsRecientes.length === 0 ? (
            <div className="state-message empty">No hay leads registrados aún.</div>
          ) : (
            <ul className="lista-reciente">
              {leadsRecientes.map((lead) => (
                <li key={lead.id} className="lista-reciente-item">
                  <div className="lista-reciente-info">
                    <span className="lista-reciente-nombre">{lead.nombre}</span>
                    <span className="lista-reciente-sub">{lead.email}</span>
                  </div>
                  <div className="lista-reciente-meta">
                    <span
                      className={`badge-priority priority-${
                        lead.prioridad ? lead.prioridad.toLowerCase() : 'media'
                      }`}
                    >
                      {lead.prioridad}
                    </span>
                    <span className="lista-reciente-fecha">
                      {lead.fecha_creacion
                        ? new Date(lead.fecha_creacion).toLocaleDateString('es-CL')
                        : '—'}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Tareas urgentes */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Tareas urgentes</h2>
            <span className="badge">Prioridad Alta</span>
          </div>
          {tareasUrgentes.length === 0 ? (
            <div className="state-message empty">No hay tareas de alta prioridad pendientes.</div>
          ) : (
            <ul className="lista-reciente">
              {tareasUrgentes.map((tarea) => {
                const vencida =
                  tarea.fecha_limite &&
                  new Date(tarea.fecha_limite + 'T00:00:00') < hoy;
                return (
                  <li key={tarea.id} className="lista-reciente-item">
                    <div className="lista-reciente-info">
                      <span className="lista-reciente-nombre">{tarea.titulo}</span>
                      <span className="lista-reciente-sub">
                        <span className={`badge-estado-tarea estado-${tarea.estado.toLowerCase().replace(' ', '-')}`}>
                          {tarea.estado}
                        </span>
                      </span>
                    </div>
                    <div className="lista-reciente-meta">
                      {tarea.fecha_limite ? (
                        <span className={vencida ? 'kpi-alerta' : 'lista-reciente-fecha'}>
                          {vencida && '⚠ '}
                          {new Date(tarea.fecha_limite + 'T00:00:00').toLocaleDateString('es-CL')}
                        </span>
                      ) : (
                        <span className="lista-reciente-fecha">Sin fecha</span>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

      </div>

    </div>
  );
}

export default Dashboard;

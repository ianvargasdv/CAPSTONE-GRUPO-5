import React from 'react';
import Icono from './Iconos';

/**
 * Vista de inicio. Está pensada para responder "qué tengo que hacer hoy"
 * antes de mostrar totales: primero los vencimientos y los leads sin contactar,
 * después la distribución general de la cartera.
 *
 * No hace llamadas al backend: trabaja con los datos ya cargados en la aplicación.
 *
 * Props:
 * - leads / propiedades / tareas: listas completas
 * - cargando: true mientras alguna de las tres sigue cargando
 * - alVerFicha: abre la ficha de un lead
 * - alEditarTarea: abre el panel de edición de una tarea
 * - alIrA: navega a una sección del sistema
 */

const MS_DIA = 86400000;

/** Convierte una diferencia de días en texto legible para el ejecutivo. */
function textoDias(dias) {
  if (dias === 0) return 'hoy';
  if (dias === 1) return 'ayer';
  return `hace ${dias} días`;
}

function fechaCorta(iso) {
  return new Date(iso + 'T00:00:00').toLocaleDateString('es-CL', {
    day: '2-digit',
    month: 'short',
  });
}

function Dashboard({ leads, propiedades, tareas, cargando, alVerFicha, alEditarTarea, alIrA }) {
  if (cargando) {
    return <div className="state-message">Cargando resumen...</div>;
  }

  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);

  // ── Leads ──
  const leadsActivos = leads.filter((l) => l.estado !== 'Cerrado');
  const leadsPorEstado = {
    Nuevo: leads.filter((l) => l.estado === 'Nuevo').length,
    Contactado: leads.filter((l) => l.estado === 'Contactado').length,
    Calificado: leads.filter((l) => l.estado === 'Calificado').length,
    Cerrado: leads.filter((l) => l.estado === 'Cerrado').length,
  };

  // Leads nuevos ordenados del más antiguo al más reciente: los que llevan
  // más tiempo sin contactar son los que se están enfriando.
  const sinContactar = leads
    .filter((l) => l.estado === 'Nuevo')
    .sort((a, b) => new Date(a.fecha_creacion) - new Date(b.fecha_creacion))
    .slice(0, 5)
    .map((lead) => ({
      ...lead,
      dias: lead.fecha_creacion
        ? Math.floor((hoy - new Date(lead.fecha_creacion).setHours(0, 0, 0, 0)) / MS_DIA)
        : 0,
    }));

  // ── Propiedades ──
  const propPorEstado = {
    Disponible: propiedades.filter((p) => p.estado === 'Disponible').length,
    Reservada: propiedades.filter((p) => p.estado === 'Reservada').length,
    Vendida: propiedades.filter((p) => p.estado === 'Vendida').length,
  };

  // ── Tareas ──
  const abiertas = tareas.filter((t) => t.estado !== 'Completada');

  const conFecha = abiertas
    .filter((t) => t.fecha_limite)
    .map((t) => ({ ...t, limite: new Date(t.fecha_limite + 'T00:00:00') }));

  const vencidas = conFecha.filter((t) => t.limite < hoy);
  const paraHoy = conFecha.filter((t) => t.limite.getTime() === hoy.getTime());
  const proximas = conFecha
    .filter((t) => t.limite > hoy && t.limite <= new Date(hoy.getTime() + 7 * MS_DIA))
    .sort((a, b) => a.limite - b.limite);

  // La agenda prioriza lo vencido, después lo de hoy y después la semana
  const agenda = [
    ...vencidas.sort((a, b) => a.limite - b.limite).map((t) => ({ t, tipo: 'vencida' })),
    ...paraHoy.map((t) => ({ t, tipo: 'hoy' })),
    ...proximas.map((t) => ({ t, tipo: 'proxima' })),
  ].slice(0, 6);

  return (
    <>
      {/* ── Indicadores ── */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="usuarios" tamano={13} />
            <span className="kpi-label">Leads activos</span>
          </div>
          <div className="kpi-numero">{leadsActivos.length}</div>
          <div className="kpi-detalle">
            {leadsPorEstado.Nuevo > 0
              ? `${leadsPorEstado.Nuevo} sin contactar`
              : 'Todos contactados'}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="edificio" tamano={13} />
            <span className="kpi-label">Disponibles</span>
          </div>
          <div className="kpi-numero">{propPorEstado.Disponible}</div>
          <div className="kpi-detalle">de {propiedades.length} en catálogo</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="tareas" tamano={13} />
            <span className="kpi-label">Por hacer</span>
          </div>
          <div className="kpi-numero">{abiertas.length}</div>
          <div className="kpi-detalle">
            {paraHoy.length > 0 ? `${paraHoy.length} vencen hoy` : 'Nada vence hoy'}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-encabezado">
            <Icono nombre="alerta" tamano={13} />
            <span className="kpi-label">Vencidas</span>
          </div>
          <div className="kpi-numero">{vencidas.length}</div>
          <div className={`kpi-detalle ${vencidas.length > 0 ? 'critico' : ''}`}>
            {vencidas.length > 0 ? 'Requieren atención' : 'Sin atrasos'}
          </div>
        </div>
      </div>

      {/* ── Operación del día ── */}
      <div className="grid-dos">
        <div className="panel">
          <div className="panel-encabezado">
            <span className="panel-titulo">Agenda</span>
            <button className="btn-secondary" onClick={() => alIrA('tareas')}>
              Ver tareas
            </button>
          </div>

          {agenda.length === 0 ? (
            <div className="state-message empty">
              <Icono nombre="check" tamano={18} />
              <span className="vacio-titulo">Nada pendiente esta semana</span>
              <span className="vacio-detalle">
                No hay tareas con vencimiento en los próximos siete días.
              </span>
            </div>
          ) : (
            <ul className="lista-simple">
              {agenda.map(({ t, tipo }) => (
                <li
                  key={t.id}
                  className="lista-simple-item clicable"
                  onClick={() => alEditarTarea(t)}
                >
                  <div className="lista-simple-info">
                    <span className="lista-simple-nombre">{t.titulo}</span>
                    <span className="lista-simple-sub">
                      {tipo === 'vencida' && 'Vencida · '}
                      {tipo === 'hoy' && 'Vence hoy · '}
                      {tipo === 'proxima' && `${fechaCorta(t.fecha_limite)} · `}
                      {t.estado}
                    </span>
                  </div>

                  <div className="lista-simple-meta">
                    {tipo === 'vencida' && (
                      <span className="etiqueta peligro">
                        <Icono nombre="alerta" tamano={11} />
                        Atrasada
                      </span>
                    )}
                    {tipo === 'hoy' && <span className="etiqueta alerta">Hoy</span>}
                    <span
                      className={`prioridad prioridad-${(t.prioridad || 'media').toLowerCase()}`}
                    >
                      <span className="prioridad-punto" />
                      {t.prioridad}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel">
          <div className="panel-encabezado">
            <span className="panel-titulo">Leads por contactar</span>
            <button className="btn-secondary" onClick={() => alIrA('leads')}>
              Ver leads
            </button>
          </div>

          {sinContactar.length === 0 ? (
            <div className="state-message empty">
              <Icono nombre="check" tamano={18} />
              <span className="vacio-titulo">Sin leads pendientes</span>
              <span className="vacio-detalle">
                Todos los prospectos registrados ya tuvieron un primer contacto.
              </span>
            </div>
          ) : (
            <ul className="lista-simple">
              {sinContactar.map((lead) => (
                <li
                  key={lead.id}
                  className="lista-simple-item clicable"
                  onClick={() => alVerFicha(lead)}
                >
                  <div className="lista-simple-info">
                    <span className="lista-simple-nombre">{lead.nombre}</span>
                    <span className="lista-simple-sub">
                      {lead.telefono || lead.email}
                    </span>
                  </div>

                  <div className="lista-simple-meta">
                    {lead.dias >= 3 && (
                      <span className="etiqueta alerta">{textoDias(lead.dias)}</span>
                    )}
                    <span
                      className={`prioridad prioridad-${(lead.prioridad || 'media').toLowerCase()}`}
                    >
                      <span className="prioridad-punto" />
                      {lead.prioridad}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* ── Distribución de la cartera ── */}
      <div className="grid-dos">
        <div className="panel">
          <div className="panel-encabezado">
            <span className="panel-titulo">Embudo de leads</span>
          </div>
          <div className="panel-cuerpo">
            <div className="distribucion-lista">
              {Object.entries(leadsPorEstado).map(([estado, cantidad]) => (
                <div key={estado} className="distribucion-item">
                  <span className="distribucion-label">{estado}</span>
                  <div className="distribucion-pista">
                    <div
                      className="distribucion-barra info"
                      style={{
                        width: leads.length > 0 ? `${(cantidad / leads.length) * 100}%` : '0%',
                      }}
                    />
                  </div>
                  <span className="distribucion-valor">{cantidad}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-encabezado">
            <span className="panel-titulo">Estado del catálogo</span>
          </div>
          <div className="panel-cuerpo">
            <div className="distribucion-lista">
              {[
                ['Disponible', propPorEstado.Disponible, 'exito'],
                ['Reservada', propPorEstado.Reservada, 'alerta'],
                ['Vendida', propPorEstado.Vendida, ''],
              ].map(([estado, cantidad, tono]) => (
                <div key={estado} className="distribucion-item">
                  <span className="distribucion-label">{estado}</span>
                  <div className="distribucion-pista">
                    <div
                      className={`distribucion-barra ${tono}`}
                      style={{
                        width:
                          propiedades.length > 0
                            ? `${(cantidad / propiedades.length) * 100}%`
                            : '0%',
                      }}
                    />
                  </div>
                  <span className="distribucion-valor">{cantidad}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Dashboard;

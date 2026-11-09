import React from 'react';

const ESTADOS = { pendiente: 'Pendiente', guardado: 'Guardado', descartado: 'Descartado' };

export default function AgendaMobilita({ conversacion, ocupado, alElegir, alDescartar, alDescartarTodos }) {
  if (!conversacion?.agenda?.length) return null;
  const pendientes = conversacion.agenda.filter(b => b.estado === 'pendiente');
  const indice = conversacion.agenda.findIndex(b => b.estado === 'pendiente');
  return <section className="mobilita-agenda" aria-label="Organización de solicitudes">
    <div className="mobilita-avance" aria-hidden="true">{conversacion.agenda.map(b => <span key={b.numero} className={`estado-${b.estado}`} />)}</div>
    <details>
      <summary>{indice >= 0 ? `Solicitud ${indice + 1} de ${conversacion.agenda.length}` : 'Solicitudes terminadas'}</summary>
      <ol>{conversacion.agenda.map(b => <li key={b.numero} aria-current={b.numero === indice + 1 ? 'step' : undefined}>
        <span className={`mobilita-paso-numero estado-${b.estado}`} aria-hidden="true">{b.numero}</span>
        <div><strong>{b.cliente}</strong><span className={`mobilita-estado estado-${b.estado}`}>{ESTADOS[b.estado]}</span>
        <small>{b.acciones.join(', ') || 'Por aclarar'}</small></div>
      </li>)}</ol>
    </details>
    {conversacion.opciones_cliente?.length > 0 && <div className="mobilita-elegir-cliente" role="group" aria-label="Elegir el cliente correcto">
      <p>¿A cuál te refieres?</p>
      {conversacion.opciones_cliente.map(c => <button key={c.id} type="button" className="btn-secondary" disabled={ocupado} onClick={() => alElegir(c.id)}>
        {c.nombre}<small>{c.correo || `Ficha ${c.id}`} · {c.estado}</small>
      </button>)}
    </div>}
    {(pendientes.length > 1 || (pendientes.length > 0 && conversacion.estado !== 'pendiente')) && <div className="mobilita-agenda-acciones">
      {pendientes.length > 0 && conversacion.estado !== 'pendiente' && <button type="button" className="btn-secondary" disabled={ocupado} onClick={alDescartar}>Omitir esta solicitud</button>}
      {pendientes.length > 1 && <button type="button" className="mobilita-accion-discreta" disabled={ocupado} onClick={alDescartarTodos}>Descartar las solicitudes pendientes</button>}
    </div>}
  </section>;
}

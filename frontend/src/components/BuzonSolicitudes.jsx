import React, { useState } from 'react';
import { resolverSolicitudArchivo } from '../api';
import Icono from './Iconos';

function Solicitud({ solicitud: s, admin, alActualizar, alVerLead }) {
  const [motivo, setMotivo] = useState('');
  const [decision, setDecision] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const resolver = async e => {
    e.preventDefault(); setOcupado(true); setError('');
    try { await resolverSolicitudArchivo(s.id, decision, motivo.trim()); setDecision(''); await alActualizar(); }
    catch (err) { setError(err.message); }
    finally { setOcupado(false); }
  };
  return <article className="solicitud-archivo">
    <header><div><h3>{s.cliente}</h3><p className="solicitud-autor">{s.autor} · {new Date(s.fecha).toLocaleDateString('es-CL')}</p></div>
      <span className={`solicitud-estado solicitud-estado-${s.estado.toLowerCase()}`}>{s.estado}</span></header>
    <div className="solicitud-motivo"><span>Motivo de la solicitud</span><p>{s.motivo}</p></div>
    {s.resolucion && <div className="solicitud-resolucion"><strong>Decisión de {s.resuelto_por}</strong><p>{s.resolucion}</p></div>}
    {s.estado === 'Pendiente' && !decision && <div className="solicitud-acciones">
      {alVerLead && <button className="btn-secondary" onClick={() => alVerLead(s.lead_id)}>Ver ficha del lead</button>}
      {admin && <div className="solicitud-botones">
        <button className="btn-primary" onClick={() => setDecision('Aprobada')}>Revisar archivo</button>
        <button className="mobilita-accion-discreta solicitud-rechazar" onClick={() => setDecision('Rechazada')}>Rechazar</button>
      </div>}
    </div>}
    {decision && <form className="solicitud-decision" onSubmit={resolver}>
      <h4>{decision === 'Aprobada' ? 'Aprobar el archivo' : 'Rechazar la solicitud'}</h4>
      <p>{decision === 'Aprobada' ? 'Se archivará el lead y quedará cerrado, conservando sus contactos, tareas y demás registros. No se eliminará nada.' : 'El lead seguirá disponible. Explica por qué rechazas la solicitud.'}</p>
      <label>Motivo de la decisión<textarea className="form-textarea" rows={3} placeholder="Explica brevemente tu decisión" required maxLength={5000} value={motivo} onChange={e => setMotivo(e.target.value)} /></label>
      <div className="solicitud-botones"><button className="btn-primary" disabled={ocupado || !motivo.trim()}>{decision === 'Aprobada' ? 'Confirmar archivo' : 'Confirmar rechazo'}</button>
        <button type="button" className="btn-secondary" disabled={ocupado} onClick={() => setDecision('')}>Cancelar</button></div>
    </form>}
    {error && <p className="alert-error" role="alert">{error}</p>}
  </article>;
}

export default function BuzonSolicitudes({ solicitudes, error, admin, alActualizar, alVerLead }) {
  const [filtro, setFiltro] = useState('Pendiente');
  const filas = solicitudes.filter(s => filtro === 'Todas' || s.estado === filtro);
  return <section className="panel buzon-solicitudes">
    <div className="buzon-cabecera"><div><span className="buzon-antetitulo">{admin ? 'Revisión de administración' : 'Seguimiento de mis solicitudes'}</span><h2>{admin ? 'Solicitudes de archivo' : 'Mis solicitudes'}</h2></div>
      <button className="btn-secondary" onClick={alActualizar}>Actualizar</button></div>
    <details className="buzon-ayuda"><summary>¿Qué ocurre al archivar un lead?</summary><p>El archivo retira el lead del listado activo y conserva su historial. Las tareas y visitas relacionadas no se cancelan automáticamente.</p></details>
    <div className="buzon-filtros"><label>Estado <select className="form-select" value={filtro} onChange={e => setFiltro(e.target.value)}>
      {['Pendiente', 'Aprobada', 'Rechazada', 'Todas'].map(e => <option key={e}>{e}</option>)}
    </select></label><span>{filas.length} {filas.length === 1 ? 'solicitud' : 'solicitudes'}</span></div>
    {error && <p className="alert-error" role="alert">{error}</p>}
    {!error && !filas.length && <div className="buzon-vacio"><span><Icono nombre="tareas" tamano={26} /></span><h3>{filtro === 'Pendiente' ? 'No quedan pendientes' : 'Sin resultados'}</h3><p>No hay solicitudes en este estado.</p></div>}
    <div className="buzon-lista">{filas.map(s => <Solicitud key={s.id} solicitud={s} admin={admin} alActualizar={alActualizar} alVerLead={alVerLead} />)}</div>
    <p className="buzon-pie">Se muestran hasta 100 solicitudes, con las pendientes primero.</p>
  </section>;
}

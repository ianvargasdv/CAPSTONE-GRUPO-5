import React, { useMemo, useState } from 'react';
import Icono from './Iconos';

export const ESTADOS_VISITA = ['Programada', 'Confirmada', 'Realizada', 'Cancelada', 'No asistió'];

const inicioSemana = (fecha) => {
  const resultado = new Date(fecha);
  resultado.setHours(0, 0, 0, 0);
  const dia = resultado.getDay() || 7;
  resultado.setDate(resultado.getDate() - dia + 1);
  return resultado;
};

const claveDia = (fecha) => {
  const local = new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
};

const hora = (iso) => new Date(iso).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
const fechaLarga = (fecha) => fecha.toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric', month: 'short' });

function TarjetaVisita({ visita, alEditar, alEliminar, alCambiarEstado }) {
  return <article className={`visita-card visita-${visita.estado.toLowerCase().replaceAll(' ', '-').replace('ó', 'o')}`}>
    <div className="visita-hora"><strong>{hora(visita.fecha_hora)}</strong><span>{visita.duracion_minutos} min</span></div>
    <span className="visita-lead">{visita.lead_nombre || 'Lead eliminado'}</span>
    <span className="visita-propiedad">{visita.propiedad_titulo || 'Propiedad eliminada'}</span>
    <span className="visita-estado">{visita.estado} · {visita.modalidad}</span>
    <div className="visita-acciones">
      <select value={visita.estado} onChange={(e) => alCambiarEstado(visita, e.target.value)} aria-label={`Estado de visita de ${visita.lead_nombre || 'lead'}`}>
        {ESTADOS_VISITA.map((estado) => <option key={estado}>{estado}</option>)}
      </select>
      <button className="btn-icono" onClick={() => alEditar(visita)} title="Editar"><Icono nombre="editar" /></button>
      <button className="btn-icono peligro" onClick={() => alEliminar(visita)} title="Eliminar"><Icono nombre="eliminar" /></button>
    </div>
  </article>;
}

function AgendaVisitas({ visitas, cargando, error, alEditar, alEliminar, alCambiarEstado }) {
  const [modo, setModo] = useState('semana');
  const [referencia, setReferencia] = useState(new Date());
  const [filtroEstado, setFiltroEstado] = useState('Todos');

  const semana = useMemo(() => {
    const inicio = inicioSemana(referencia);
    return Array.from({ length: 7 }, (_, indice) => {
      const dia = new Date(inicio);
      dia.setDate(inicio.getDate() + indice);
      return dia;
    });
  }, [referencia]);

  if (cargando) return <div className="state-message">Cargando agenda...</div>;
  if (error) return <div className="panel-cuerpo"><div className="alert-error"><Icono nombre="alerta" />{error}</div></div>;

  const filtradas = visitas.filter((v) => filtroEstado === 'Todos' || v.estado === filtroEstado);
  const hoy = claveDia(new Date());
  const deHoy = visitas.filter((v) => claveDia(new Date(v.fecha_hora)) === hoy && !['Cancelada', 'No asistió'].includes(v.estado));
  const proximas = visitas.filter((v) => new Date(v.fecha_hora) >= new Date() && !['Cancelada', 'No asistió'].includes(v.estado));
  const moverSemana = (dias) => setReferencia((actual) => new Date(actual.getFullYear(), actual.getMonth(), actual.getDate() + dias));

  return <>
    <div className="agenda-resumen">
      <div><span>Visitas hoy</span><strong>{deHoy.length}</strong></div>
      <div><span>Próximas</span><strong>{proximas.length}</strong></div>
      <div><span>Confirmadas</span><strong>{visitas.filter((v) => v.estado === 'Confirmada').length}</strong></div>
      <div><span>Realizadas</span><strong>{visitas.filter((v) => v.estado === 'Realizada').length}</strong></div>
    </div>
    <div className="barra-herramientas agenda-herramientas">
      <div className="agenda-navegacion"><button className="btn-secondary" onClick={() => moverSemana(-7)}>←</button><button className="btn-secondary" onClick={() => setReferencia(new Date())}>Hoy</button><button className="btn-secondary" onClick={() => moverSemana(7)}>→</button></div>
      <span className="agenda-rango">{semana[0].toLocaleDateString('es-CL')} – {semana[6].toLocaleDateString('es-CL')}</span>
      <select className="filter-select" value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}><option>Todos</option>{ESTADOS_VISITA.map((estado) => <option key={estado}>{estado}</option>)}</select>
      <div className="selector-vista"><button className={modo === 'semana' ? 'activo' : ''} onClick={() => setModo('semana')}>Semana</button><button className={modo === 'lista' ? 'activo' : ''} onClick={() => setModo('lista')}>Lista</button></div>
    </div>

    {visitas.length === 0 ? <div className="state-message empty"><Icono nombre="calendario" tamano={20} /><span className="vacio-titulo">No hay visitas agendadas</span><span className="vacio-detalle">Agenda una visita vinculada a un lead y una propiedad.</span></div>
      : modo === 'semana' ? <div className="agenda-semana">{semana.map((dia) => {
        const items = filtradas.filter((v) => claveDia(new Date(v.fecha_hora)) === claveDia(dia));
        return <section className={`agenda-dia ${claveDia(dia) === hoy ? 'hoy' : ''}`} key={claveDia(dia)}><div className="agenda-dia-titulo"><span>{fechaLarga(dia)}</span><span>{items.length}</span></div><div className="agenda-dia-lista">{items.map((v) => <TarjetaVisita key={v.id} visita={v} alEditar={alEditar} alEliminar={alEliminar} alCambiarEstado={alCambiarEstado} />)}{items.length === 0 && <span className="agenda-vacio">Sin visitas</span>}</div></section>;
      })}</div>
      : <div className="table-wrapper"><table className="leads-table"><thead><tr><th>Fecha</th><th>Lead / propiedad</th><th>Estado</th><th>Modalidad</th><th>Responsable</th><th /></tr></thead><tbody>{filtradas.map((v) => <tr key={v.id}><td className="col-fecha">{new Date(v.fecha_hora).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })}</td><td><div className="celda-doble"><span className="celda-principal">{v.lead_nombre || 'Lead eliminado'}</span><span className="celda-secundaria">{v.propiedad_titulo || 'Propiedad eliminada'}</span></div></td><td><select className="select-celda" value={v.estado} onChange={(e) => alCambiarEstado(v, e.target.value)}>{ESTADOS_VISITA.map((estado) => <option key={estado}>{estado}</option>)}</select></td><td>{v.modalidad}</td><td>{v.ejecutivo_nombre || 'Sin asignar'}</td><td className="col-acciones"><div className="acciones-celda"><button className="btn-icono" onClick={() => alEditar(v)}><Icono nombre="editar" /></button><button className="btn-icono peligro" onClick={() => alEliminar(v)}><Icono nombre="eliminar" /></button></div></td></tr>)}</tbody></table></div>}
  </>;
}

export default AgendaVisitas;

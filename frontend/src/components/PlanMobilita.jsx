import React, { useEffect, useRef } from 'react';
import Icono from './Iconos';

const CAMPOS = {
  nombre: 'Nombre', email: 'Correo', telefono: 'Teléfono',
  tipo: 'Tipo de contacto', notas: 'Notas', estado: 'Estado', prioridad: 'Prioridad',
  titulo: 'Título', descripcion: 'Descripción', fecha_limite: 'Fecha límite',
  fecha_hora: 'Fecha y hora', modalidad: 'Modalidad', duracion_minutos: 'Duración (minutos)',
  punto_encuentro: 'Punto de encuentro', nivel_interes: 'Interés', motivo: 'Motivo',
  proxima_accion: 'Próximo seguimiento', fecha_proxima_accion: 'Fecha de seguimiento',
  tipo_operacion: 'Operación', presupuesto_min: 'Presupuesto mínimo', presupuesto_max: 'Presupuesto máximo',
  moneda: 'Moneda', comunas_interes: 'Comunas', tipo_propiedad_buscada: 'Tipo de propiedad',
  dormitorios_min: 'Dormitorios mínimos', banos_min: 'Baños mínimos', plazo_decision: 'Plazo', financiamiento: 'Financiamiento',
};

export default function PlanMobilita({ propuesta, pendientes = [], ocupado, error, alConfirmar, alDescartar, alAjustar }) {
  const aviso = useRef(null);
  const encabezado = useRef(null);
  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      encabezado.current?.scrollIntoView({ block: 'start' });
      encabezado.current?.focus({ preventScroll: true });
    });
    return () => cancelAnimationFrame(frame);
  }, []);
  useEffect(() => {
    if (error) { aviso.current?.scrollIntoView({ block: 'nearest' }); aviso.current?.focus({ preventScroll: true }); }
  }, [error]);
  return <section className="mobilita-plan" aria-label="Revisar cambios propuestos">
    <header className="mobilita-plan-cabecera">
      <span className="mobilita-plan-icono"><Icono nombre="tareas" tamano={20} /></span>
      <div><h3 ref={encabezado} tabIndex={-1}>Revisar cambios</h3><strong>{propuesta.cliente_acciones}</strong></div>
    </header>
    <p className="mobilita-plan-intro">Todavía no se ha guardado nada. Revisa los datos antes de confirmar.</p>
    {pendientes.length > 0 && propuesta.acciones.some(o => o.tipo === 'crear_tarea') && <aside className="chat-tareas-pendientes">
      <strong>Este lead ya tiene tareas pendientes</strong>
      <ul>{pendientes.slice(0, 5).map(t => <li key={t.id}>{t.titulo}</li>)}</ul>
      {pendientes.length > 5 && <p>Hay {pendientes.length - 5} más en Tareas.</p>}
      <p>Si es el mismo seguimiento, descarta esta propuesta y pide actualizar la tarea existente.</p>
    </aside>}
    <div className="mobilita-plan-lista">{propuesta.acciones.map((op, i) => <article className="mobilita-plan-accion" style={{ '--orden': i }} key={i}>
      <div className="mobilita-plan-accion-titulo"><span aria-hidden="true">{i + 1}</span><h4>{op.etiqueta}</h4></div>
      {op.referencia && <p className="mobilita-plan-referencia">{op.referencia}</p>}
      <dl>{Object.entries(op.datos).map(([k, v]) => <div className="mobilita-plan-dato" key={k}>
        <dt>{CAMPOS[k] || k}</dt><dd>{op.antes && typeof op.antes === 'object' && k in op.antes && <small>Actual: {op.antes[k] === 'None' ? 'Sin registrar' : op.antes[k]}</small>}
          <span>{v == null ? 'Sin valor' : String(v)}</span></dd>
      </div>)}</dl>
      {op.tipo === 'solicitar_archivo' && <p className="mobilita-plan-nota">El lead seguirá intacto hasta que administración decida. Aprobar archiva, sin borrar el historial.</p>}
      {op.tipo === 'crear_tarea' && <p className="mobilita-plan-nota">Se guardará como Pendiente.</p>}
    </article>)}</div>
    {error && <p ref={aviso} tabIndex={-1} className="alert-error" role="alert">{error}</p>}
    <footer className="mobilita-plan-pie">
      <p>Propuesta válida por 30 minutos.</p>
      <button type="button" className="btn-primary" disabled={ocupado} onClick={alConfirmar}>{ocupado ? 'Guardando…' : 'Confirmar cambios'}</button>
      <div className="mobilita-plan-secundarias">
        {alAjustar && <button type="button" className="btn-secondary" disabled={ocupado} onClick={alAjustar}>Corregir esta solicitud</button>}
        <button type="button" className="mobilita-accion-discreta" disabled={ocupado} onClick={alDescartar}>Descartar propuesta</button>
      </div>
    </footer>
  </section>;
}

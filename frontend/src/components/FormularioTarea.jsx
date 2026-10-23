import React, { useState, useEffect, useRef } from 'react';
import { clienteDeTarea, fechaDeTarea } from '../presentacion';
import { pendientesDelLead, firmaPendientes, validarNuevaTareaIA } from '../tareaDesdeIA';

/**
 * Formulario para crear o editar una tarea. Se muestra dentro de un panel lateral.
 *
 * Props:
 * - alGuardar: función que recibe los datos del formulario
 * - tareaEditar: tarea con datos precargados en modo edición (opcional)
 * - alCancelar: cierra el panel sin guardar
 * - leads: lista de leads disponibles para vincular
 */
function FormularioTarea({ alGuardar, tareaEditar, alCancelar, leads = [], borradorIA, tareasRelacionadas = [], alAbrirPendiente, contextoIA }) {
  const envioEnCurso = useRef(false);
  const [titulo, setTitulo] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [estado, setEstado] = useState('Pendiente');
  const [prioridad, setPrioridad] = useState('Media');
  const [fechaLimite, setFechaLimite] = useState('');
  const [leadId, setLeadId] = useState(() => String((tareaEditar || borradorIA)?.lead_id || ''));
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [crearDistinta, setCrearDistinta] = useState(false);
  const [confirmarDistinta, setConfirmarDistinta] = useState(false);

  const modoEdicion = Boolean(tareaEditar);
  const nombreCliente = clienteDeTarea(leadId, leads);
  const pendientes = borradorIA ? pendientesDelLead(tareasRelacionadas, borradorIA.lead_id) : [];
  const requiereDecision = Boolean(borradorIA && !modoEdicion && pendientes.length);
  const mostrarFormulario = !requiereDecision || crearDistinta;
  const firmaActual = borradorIA ? firmaPendientes(tareasRelacionadas, borradorIA.lead_id) : '';

  useEffect(() => {
    setCrearDistinta(false);
    setConfirmarDistinta(false);
  }, [tareaEditar, borradorIA, firmaActual]);

  useEffect(() => {
    const inicial = tareaEditar || borradorIA;
    if (inicial) {
      setTitulo(inicial.titulo || '');
      setDescripcion(inicial.descripcion || '');
      setEstado(inicial.estado || 'Pendiente');
      setPrioridad(inicial.prioridad || 'Media');
      setFechaLimite(inicial.fecha_limite || '');
      setLeadId(inicial.lead_id ? String(inicial.lead_id) : '');
    } else {
      setTitulo('');
      setDescripcion('');
      setEstado('Pendiente');
      setPrioridad('Media');
      setFechaLimite('');
      setLeadId('');
    }
    setError(null);
  }, [tareaEditar, borradorIA]);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (envioEnCurso.current) return;
    if (!titulo.trim()) {
      setError('El título de la tarea es obligatorio');
      return;
    }

    try {
      const datos = {
        titulo: titulo.trim(), descripcion: descripcion.trim() || null,
        estado, prioridad, fecha_limite: fechaLimite || null,
        lead_id: leadId ? parseInt(leadId, 10) : null,
      };
      validarNuevaTareaIA(borradorIA, tareasRelacionadas, datos, {crearDistinta, confirmarDistinta});
      envioEnCurso.current = true;
      setCargando(true);
      setError(null);
      await alGuardar(datos, {crearDistinta, confirmarDistinta});
    } catch (err) {
      setError(err.message || 'No se pudo guardar la tarea');
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      <section className="tarea-contexto" aria-label="Cliente de la tarea">
        <span className="form-ayuda">Cliente</span>
        <strong>{nombreCliente}</strong>
        <span className="form-ayuda">
          {modoEdicion ? `Tarea existente: ${tareaEditar.titulo}` : requiereDecision && !crearDistinta ? 'Revisa el seguimiento pendiente antes de crear otra tarea' : borradorIA ? 'Nueva tarea a partir de una recomendación' : 'Nueva tarea'}
        </span>
      </section>
      {error && <div className="alert-error">{error}</div>}

      {contextoIA && (
        <div className="panel">
          <p>Estás editando una tarea existente. Sus datos se conservan; sólo cambiarán si editas y pulsas Guardar cambios.</p>
          <details>
            <summary>Ver la propuesta de IA como referencia</summary>
            <p className="resumen-texto">{contextoIA}</p>
          </details>
        </div>
      )}

      {borradorIA && (
        <div className="panel">
          <p>{requiereDecision
            ? 'Este cliente ya tiene seguimiento pendiente. Si la recomendación propone retomarlo, abre la tarea existente: no necesitas crear otra.'
            : 'Revisa la propuesta de IA antes de guardar. Guardar crea una tarea; no contacta al cliente ni agenda una visita.'}</p>
          {pendientes.length ? (
            <ul>{pendientes.map((tarea) => (
              <li key={tarea.id}>
                <strong>{clienteDeTarea(tarea.lead_id, leads)}</strong> · {tarea.titulo}
                <div className="form-ayuda">{tarea.estado} · {fechaDeTarea(tarea.fecha_limite)}</div>
                {tarea.descripcion && <p className="resumen-texto">{tarea.descripcion}</p>}
                {alAbrirPendiente && <button type="button" className="btn-primary"
                  disabled={cargando} onClick={() => alAbrirPendiente(tarea.id)}
                  aria-label={`Abrir tarea existente: ${tarea.titulo} · ${clienteDeTarea(tarea.lead_id, leads)}`}>Abrir tarea existente</button>}
              </li>
            ))}</ul>
          ) : <p>No hay tareas pendientes registradas al abrir este formulario.</p>}
          <details>
            <summary>Ver la recomendación como referencia</summary>
            <p className="resumen-texto">{borradorIA.descripcion}</p>
          </details>
          {requiereDecision && !crearDistinta && <button type="button" className="btn-secondary"
            onClick={() => {setCrearDistinta(true); setTitulo(''); setDescripcion(''); setError(null);}}>
            Necesito crear una acción distinta
          </button>}
        </div>
      )}

      {mostrarFormulario && <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="titulo-tarea">Título *</label>
          <input
            id="titulo-tarea"
            type="text"
            required
            maxLength={200}
            placeholder="Llamar para agendar visita"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            disabled={cargando}
            autoFocus
          />
        </div>

        <div className="form-group">
          <label htmlFor="prioridad-tarea">Prioridad</label>
          <select
            id="prioridad-tarea"
            value={prioridad}
            onChange={(e) => setPrioridad(e.target.value)}
            disabled={cargando}
          >
            <option value="Alta">Alta</option>
            <option value="Media">Media</option>
            <option value="Baja">Baja</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="estado-tarea">Estado</label>
          <select
            id="estado-tarea"
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            disabled={cargando}
          >
            <option value="Pendiente">Pendiente</option>
            <option value="En Progreso">En Progreso</option>
            <option value="Completada">Completada</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="fecha-limite">Fecha límite</label>
          <input
            id="fecha-limite"
            type="date"
            value={fechaLimite}
            onChange={(e) => setFechaLimite(e.target.value)}
            disabled={cargando}
          />
        </div>

        <div className="form-group">
          <label htmlFor={borradorIA || contextoIA ? undefined : 'lead-tarea'}>Cliente asociado</label>
          {borradorIA || contextoIA ? <p className="form-cliente-fijo">{nombreCliente}</p> : <select
            id="lead-tarea"
            value={leadId}
            onChange={(e) => setLeadId(e.target.value)}
            disabled={cargando || Boolean(borradorIA)}
          >
            <option value="">Ninguno</option>
            {leadId && !leads.some((lead) => String(lead.id) === leadId) && (
              <option value={leadId}>Cliente no disponible</option>
            )}
            {leads.map((lead) => (
              <option key={lead.id} value={lead.id}>
                {lead.nombre}
              </option>
            ))}
          </select>}
        </div>

        <div className="form-group form-group-full">
          <label htmlFor="descripcion-tarea">Descripción{requiereDecision && crearDistinta ? ' *' : ''}</label>
          <textarea
            id="descripcion-tarea"
            className="form-textarea"
            placeholder={requiereDecision && crearDistinta ? 'Explica qué acción nueva realizarás, distinta de las tareas pendientes' : 'Detalles adicionales de la tarea'}
            required={requiereDecision && crearDistinta}
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            disabled={cargando}
            rows={3}
            maxLength={5000}
          />
        </div>
      </div>}

      {requiereDecision && crearDistinta && <label className="filtro-casilla">
        <input type="checkbox" checked={confirmarDistinta} disabled={cargando}
          onChange={e => setConfirmarDistinta(e.target.checked)} />
        Revisé los pendientes y esta tarea corresponde a una acción distinta.
      </label>}

      <div className="form-actions">
        {alCancelar && (
          <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>
            Cancelar
          </button>
        )}
        {requiereDecision && crearDistinta && <button type="button" className="btn-secondary" disabled={cargando}
          onClick={() => {setCrearDistinta(false);setConfirmarDistinta(false);setError(null);}}>
          Volver a las tareas pendientes
        </button>}
        {mostrarFormulario && <button type="submit" className="btn-primary" disabled={cargando || (requiereDecision && !confirmarDistinta)}>
          {cargando ? 'Guardando...' : modoEdicion ? 'Guardar cambios' : 'Crear tarea'}
        </button>}
      </div>
    </form>
  );
}

export default FormularioTarea;

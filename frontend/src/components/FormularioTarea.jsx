import React, { useState, useEffect, useRef } from 'react';

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
  const [leadId, setLeadId] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const modoEdicion = Boolean(tareaEditar);

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
      envioEnCurso.current = true;
      setCargando(true);
      setError(null);
      await alGuardar({
        titulo: titulo.trim(),
        descripcion: descripcion.trim() || null,
        estado,
        prioridad,
        fecha_limite: fechaLimite || null,
        lead_id: leadId ? parseInt(leadId, 10) : null,
      });
    } catch (err) {
      setError(err.message || 'No se pudo guardar la tarea');
    } finally {
      envioEnCurso.current = false;
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
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
          <p>Revisa la propuesta de IA. Elige el título, la prioridad y, si corresponde, una fecha.
            Guardar crea una tarea; no contacta al cliente ni agenda una visita.</p>
          <p>Si la recomendación corresponde a una de estas tareas, ábrela en vez de crear otra:</p>
          {tareasRelacionadas.length ? (
            <ul>{tareasRelacionadas.map((tarea) => (
              <li key={tarea.id}>
                {tarea.titulo} · {tarea.estado}{tarea.fecha_limite ? ` · ${tarea.fecha_limite}` : ''}{' '}
                {alAbrirPendiente && <button type="button" className="btn-secondary"
                  disabled={cargando} onClick={() => alAbrirPendiente(tarea.id)}
                  aria-label={`Abrir tarea existente: ${tarea.titulo}`}>Abrir tarea existente</button>}
              </li>
            ))}</ul>
          ) : <p>No hay tareas pendientes registradas al abrir este formulario.</p>}
        </div>
      )}

      <div className="form-grid">
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
          <label htmlFor="lead-tarea">Lead asociado</label>
          <select
            id="lead-tarea"
            value={leadId}
            onChange={(e) => setLeadId(e.target.value)}
            disabled={cargando || Boolean(borradorIA)}
          >
            <option value="">Ninguno</option>
            {leads.map((lead) => (
              <option key={lead.id} value={lead.id}>
                {lead.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group form-group-full">
          <label htmlFor="descripcion-tarea">Descripción</label>
          <textarea
            id="descripcion-tarea"
            className="form-textarea"
            placeholder="Detalles adicionales de la tarea"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            disabled={cargando}
            rows={3}
            maxLength={5000}
          />
        </div>
      </div>

      <div className="form-actions">
        {alCancelar && (
          <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : modoEdicion ? 'Guardar cambios' : 'Crear tarea'}
        </button>
      </div>
    </form>
  );
}

export default FormularioTarea;

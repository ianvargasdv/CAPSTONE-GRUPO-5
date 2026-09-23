import React, { useState, useEffect } from 'react';

/**
 * Formulario para crear o editar una tarea. Se muestra dentro de un panel lateral.
 *
 * Props:
 * - alGuardar: función que recibe los datos del formulario
 * - tareaEditar: tarea con datos precargados en modo edición (opcional)
 * - alCancelar: cierra el panel sin guardar
 * - leads: lista de leads disponibles para vincular
 */
function FormularioTarea({ alGuardar, tareaEditar, alCancelar, leads = [] }) {
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
    if (tareaEditar) {
      setTitulo(tareaEditar.titulo || '');
      setDescripcion(tareaEditar.descripcion || '');
      setEstado(tareaEditar.estado || 'Pendiente');
      setPrioridad(tareaEditar.prioridad || 'Media');
      setFechaLimite(tareaEditar.fecha_limite || '');
      setLeadId(tareaEditar.lead_id ? String(tareaEditar.lead_id) : '');
    } else {
      setTitulo('');
      setDescripcion('');
      setEstado('Pendiente');
      setPrioridad('Media');
      setFechaLimite('');
      setLeadId('');
    }
    setError(null);
  }, [tareaEditar]);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (!titulo.trim()) {
      setError('El título de la tarea es obligatorio');
      return;
    }

    try {
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
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      {error && <div className="alert-error">{error}</div>}

      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="titulo-tarea">Título</label>
          <input
            id="titulo-tarea"
            type="text"
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
            disabled={cargando}
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

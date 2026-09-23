import React, { useState, useEffect } from 'react';

/**
 * Formulario para crear o editar un lead. Se muestra dentro de un panel lateral.
 *
 * Props:
 * - alGuardar: función que recibe los datos del formulario
 * - leadEditar: lead con datos precargados cuando se está editando (opcional)
 * - alCancelar: cierra el panel sin guardar
 */
function FormularioLead({ alGuardar, leadEditar, alCancelar }) {
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [telefono, setTelefono] = useState('');
  const [estado, setEstado] = useState('Nuevo');
  const [prioridad, setPrioridad] = useState('Media');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const modoEdicion = Boolean(leadEditar);

  useEffect(() => {
    if (leadEditar) {
      setNombre(leadEditar.nombre || '');
      setEmail(leadEditar.email || '');
      setTelefono(leadEditar.telefono || '');
      setEstado(leadEditar.estado || 'Nuevo');
      setPrioridad(leadEditar.prioridad || 'Media');
    } else {
      setNombre('');
      setEmail('');
      setTelefono('');
      setEstado('Nuevo');
      setPrioridad('Media');
    }
    setError(null);
  }, [leadEditar]);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (!nombre.trim() || !email.trim()) {
      setError('El nombre y el correo son obligatorios');
      return;
    }

    try {
      setCargando(true);
      setError(null);
      await alGuardar({
        nombre: nombre.trim(),
        email: email.trim(),
        telefono: telefono.trim() || null,
        estado,
        prioridad,
      });
    } catch (err) {
      setError(err.message || 'No se pudo guardar el lead');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      {error && <div className="alert-error">{error}</div>}

      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="nombre">Nombre completo</label>
          <input
            id="nombre"
            type="text"
            placeholder="Juan Pérez"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            disabled={cargando}
            autoFocus
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Correo</label>
          <input
            id="email"
            type="email"
            placeholder="juan@ejemplo.cl"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={cargando}
          />
        </div>

        <div className="form-group">
          <label htmlFor="telefono">Teléfono</label>
          <input
            id="telefono"
            type="text"
            placeholder="+56 9 1234 5678"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            disabled={cargando}
          />
        </div>

        <div className="form-group">
          <label htmlFor="estado">Estado</label>
          <select
            id="estado"
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            disabled={cargando}
          >
            <option value="Nuevo">Nuevo</option>
            <option value="Contactado">Contactado</option>
            <option value="Calificado">Calificado</option>
            <option value="Cerrado">Cerrado</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="prioridad">Prioridad</label>
          <select
            id="prioridad"
            value={prioridad}
            onChange={(e) => setPrioridad(e.target.value)}
            disabled={cargando}
          >
            <option value="Alta">Alta</option>
            <option value="Media">Media</option>
            <option value="Baja">Baja</option>
          </select>
        </div>
      </div>

      <div className="form-actions">
        {alCancelar && (
          <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : modoEdicion ? 'Guardar cambios' : 'Crear lead'}
        </button>
      </div>
    </form>
  );
}

export default FormularioLead;

import React, { useState } from 'react';

function FormularioLead({ alGuardar }) {
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [telefono, setTelefono] = useState('');
  const [estado, setEstado] = useState('Nuevo');
  const [prioridad, setPrioridad] = useState('Media');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (!nombre.trim() || !email.trim()) {
      setError('Por favor completa el nombre y el correo electrónico');
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

      // Limpiar el formulario tras guardar exitosamente
      setNombre('');
      setEmail('');
      setTelefono('');
      setEstado('Nuevo');
      setPrioridad('Media');
    } catch (err) {
      setError(err.message || 'Error al intentar guardar el lead');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      <h3 className="section-subtitle">Registrar Nuevo Lead</h3>

      {error && <div className="alert-error">{error}</div>}

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="nombre">Nombre Completo *</label>
          <input
            id="nombre"
            type="text"
            placeholder="Ej: Juan Pérez"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            disabled={cargando}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Correo Electrónico *</label>
          <input
            id="email"
            type="email"
            placeholder="Ej: juan@ejemplo.cl"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={cargando}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="telefono">Teléfono</label>
          <input
            id="telefono"
            type="text"
            placeholder="Ej: +56912345678"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            disabled={cargando}
          />
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
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : 'Guardar Lead'}
        </button>
      </div>
    </form>
  );
}

export default FormularioLead;

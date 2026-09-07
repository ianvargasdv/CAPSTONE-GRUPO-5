import React, { useState } from 'react';

/**
 * Formulario para registrar una nueva interacción con un lead.
 *
 * Props:
 * - leadNombre: nombre del lead para mostrar en el título
 * - alGuardar: función que recibe { tipo, notas } y llama al backend
 */
function FormularioInteraccion({ leadNombre, alGuardar }) {
  const [tipo, setTipo] = useState('Llamada');
  const [notas, setNotas] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (!tipo) {
      setError('Selecciona un tipo de interacción');
      return;
    }

    try {
      setCargando(true);
      setError(null);
      await alGuardar({ tipo, notas: notas.trim() || null });
      // Limpiar formulario tras guardar
      setTipo('Llamada');
      setNotas('');
    } catch (err) {
      setError(err.message || 'Error al registrar la interacción');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      <h3 className="section-subtitle">
        Registrar interacción con {leadNombre}
      </h3>

      {error && <div className="alert-error">{error}</div>}

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="tipo-interaccion">Tipo de contacto</label>
          <select
            id="tipo-interaccion"
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            disabled={cargando}
          >
            <option value="Llamada">Llamada</option>
            <option value="Email">Email</option>
            <option value="Visita">Visita</option>
            <option value="WhatsApp">WhatsApp</option>
          </select>
        </div>

        <div className="form-group form-group-full">
          <label htmlFor="notas-interaccion">Notas</label>
          <textarea
            id="notas-interaccion"
            className="form-textarea"
            placeholder="Ej: Cliente interesado en el departamento de Providencia, solicita visita el viernes."
            value={notas}
            onChange={(e) => setNotas(e.target.value)}
            disabled={cargando}
            rows={3}
          />
        </div>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : 'Registrar Interacción'}
        </button>
      </div>
    </form>
  );
}

export default FormularioInteraccion;

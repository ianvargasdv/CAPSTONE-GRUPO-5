import React, { useState } from 'react';

/**
 * Formulario compacto para registrar una interacción con un lead.
 * Se usa dentro de la ficha del lead, junto al historial.
 *
 * Props:
 * - alGuardar: función que recibe { tipo, notas }
 */
function FormularioInteraccion({ alGuardar }) {
  const [tipo, setTipo] = useState('Llamada');
  const [notas, setNotas] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const manejarEnvio = async (e) => {
    e.preventDefault();

    try {
      setCargando(true);
      setError(null);
      await alGuardar({ tipo, notas: notas.trim() || null });
      setTipo('Llamada');
      setNotas('');
    } catch (err) {
      setError(err.message || 'No se pudo registrar la interacción');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
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
            placeholder="Qué se conversó, qué quedó pendiente"
            value={notas}
            onChange={(e) => setNotas(e.target.value)}
            disabled={cargando}
            rows={2}
          />
        </div>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : 'Registrar interacción'}
        </button>
      </div>
    </form>
  );
}

export default FormularioInteraccion;

import React, { useState } from 'react';

function FormularioPropiedad({ alGuardar }) {
  const [titulo, setTitulo] = useState('');
  const [tipo, setTipo] = useState('Departamento');
  const [precio, setPrecio] = useState('');
  const [direccion, setDireccion] = useState('');
  const [estado, setEstado] = useState('Disponible');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const manejarEnvio = async (e) => {
    e.preventDefault();
    if (!titulo.trim() || !direccion.trim() || !precio) {
      setError('El título, la dirección y el precio son obligatorios');
      return;
    }

    try {
      setCargando(true);
      setError(null);
      await alGuardar({
        titulo: titulo.trim(),
        tipo,
        precio: parseInt(precio, 10),
        direccion: direccion.trim(),
        estado,
      });

      // Limpiar formulario tras guardar
      setTitulo('');
      setTipo('Departamento');
      setPrecio('');
      setDireccion('');
      setEstado('Disponible');
    } catch (err) {
      setError(err.message || 'Error al registrar la propiedad');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      <h3 className="section-subtitle">Registrar Nueva Propiedad</h3>

      {error && <div className="alert-error">{error}</div>}

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="titulo">Título de la Propiedad *</label>
          <input
            id="titulo"
            type="text"
            placeholder="Ej: Depto 2D/2B Metro Providencia"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            disabled={cargando}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="tipo">Tipo de Inmueble</label>
          <select
            id="tipo"
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            disabled={cargando}
          >
            <option value="Departamento">Departamento</option>
            <option value="Casa">Casa</option>
            <option value="Terreno">Terreno</option>
            <option value="Oficina">Oficina</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="precio">Precio (UF / CLP) *</label>
          <input
            id="precio"
            type="number"
            placeholder="Ej: 3500"
            value={precio}
            onChange={(e) => setPrecio(e.target.value)}
            disabled={cargando}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="direccion">Dirección *</label>
          <input
            id="direccion"
            type="text"
            placeholder="Ej: Av. Providencia 1234"
            value={direccion}
            onChange={(e) => setDireccion(e.target.value)}
            disabled={cargando}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="estado_prop">Estado</label>
          <select
            id="estado_prop"
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            disabled={cargando}
          >
            <option value="Disponible">Disponible</option>
            <option value="Reservada">Reservada</option>
            <option value="Vendida">Vendida</option>
          </select>
        </div>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : 'Guardar Propiedad'}
        </button>
      </div>
    </form>
  );
}

export default FormularioPropiedad;

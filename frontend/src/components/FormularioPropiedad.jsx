import React, { useState, useEffect } from 'react';

/**
 * Formulario para crear o editar una propiedad. Se muestra dentro de un panel lateral.
 *
 * Props:
 * - alGuardar: función que recibe los datos del formulario
 * - propiedadEditar: propiedad con datos precargados en modo edición (opcional)
 * - alCancelar: cierra el panel sin guardar
 */
function FormularioPropiedad({ alGuardar, propiedadEditar, alCancelar }) {
  const [titulo, setTitulo] = useState('');
  const [tipo, setTipo] = useState('Departamento');
  const [tipoOperacion, setTipoOperacion] = useState('Compra');
  const [precio, setPrecio] = useState('');
  const [moneda, setMoneda] = useState('CLP');
  const [direccion, setDireccion] = useState('');
  const [comuna, setComuna] = useState('');
  const [dormitorios, setDormitorios] = useState('');
  const [banos, setBanos] = useState('');
  const [estado, setEstado] = useState('Disponible');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const modoEdicion = Boolean(propiedadEditar);

  useEffect(() => {
    if (propiedadEditar) {
      setTitulo(propiedadEditar.titulo || '');
      setTipo(propiedadEditar.tipo || 'Departamento');
      setTipoOperacion(propiedadEditar.tipo_operacion || 'Compra');
      setPrecio(propiedadEditar.precio?.toString() || '');
      setMoneda(propiedadEditar.moneda || 'CLP');
      setDireccion(propiedadEditar.direccion || '');
      setComuna(propiedadEditar.comuna || '');
      setDormitorios(propiedadEditar.dormitorios?.toString() ?? '');
      setBanos(propiedadEditar.banos?.toString() ?? '');
      setEstado(propiedadEditar.estado || 'Disponible');
    } else {
      setTitulo('');
      setTipo('Departamento');
      setTipoOperacion('Compra');
      setPrecio('');
      setMoneda('CLP');
      setDireccion('');
      setComuna('');
      setDormitorios('');
      setBanos('');
      setEstado('Disponible');
    }
    setError(null);
  }, [propiedadEditar]);

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
        tipo_operacion: tipoOperacion,
        precio: parseInt(precio, 10),
        moneda,
        direccion: direccion.trim(),
        comuna: comuna.trim() || null,
        dormitorios: dormitorios === '' ? null : parseInt(dormitorios, 10),
        banos: banos === '' ? null : parseInt(banos, 10),
        estado,
      });
    } catch (err) {
      setError(err.message || 'No se pudo guardar la propiedad');
    } finally {
      setCargando(false);
    }
  };

  return (
    <form className="form-lead" onSubmit={manejarEnvio}>
      {error && <div className="alert-error">{error}</div>}

      <div className="form-grid">
        <div className="form-group form-group-full">
          <label htmlFor="titulo">Título</label>
          <input
            id="titulo"
            type="text"
            placeholder="Depto 2D/2B Metro Providencia"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            disabled={cargando}
            autoFocus
          />
        </div>

        <div className="form-group">
          <label htmlFor="tipo">Tipo</label>
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
          <label htmlFor="tipo_operacion_prop">Operación</label>
          <select id="tipo_operacion_prop" value={tipoOperacion} onChange={(e) => setTipoOperacion(e.target.value)} disabled={cargando}>
            <option value="Compra">Venta</option>
            <option value="Arriendo">Arriendo</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="precio">Precio</label>
          <input
            id="precio"
            type="number"
            placeholder="3500"
            value={precio}
            onChange={(e) => setPrecio(e.target.value)}
            disabled={cargando}
          />
        </div>

        <div className="form-group">
          <label htmlFor="moneda_prop">Moneda</label>
          <select id="moneda_prop" value={moneda} onChange={(e) => setMoneda(e.target.value)} disabled={cargando}>
            <option value="CLP">CLP</option>
            <option value="UF">UF</option>
          </select>
        </div>

        <div className="form-group form-group-full">
          <label htmlFor="direccion">Dirección</label>
          <input
            id="direccion"
            type="text"
            placeholder="Av. Providencia 1234, Providencia"
            value={direccion}
            onChange={(e) => setDireccion(e.target.value)}
            disabled={cargando}
          />
        </div>

        <div className="form-group">
          <label htmlFor="comuna_prop">Comuna</label>
          <input id="comuna_prop" value={comuna} onChange={(e) => setComuna(e.target.value)} disabled={cargando} placeholder="Providencia" />
        </div>

        <div className="form-group">
          <label htmlFor="dormitorios_prop">Dormitorios</label>
          <input id="dormitorios_prop" type="number" min="0" max="20" value={dormitorios} onChange={(e) => setDormitorios(e.target.value)} disabled={cargando} />
        </div>

        <div className="form-group">
          <label htmlFor="banos_prop">Baños</label>
          <input id="banos_prop" type="number" min="0" max="20" value={banos} onChange={(e) => setBanos(e.target.value)} disabled={cargando} />
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
        {alCancelar && (
          <button type="button" className="btn-secondary" onClick={alCancelar} disabled={cargando}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn-primary" disabled={cargando}>
          {cargando ? 'Guardando...' : modoEdicion ? 'Guardar cambios' : 'Crear propiedad'}
        </button>
      </div>
    </form>
  );
}

export default FormularioPropiedad;

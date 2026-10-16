import React, { useState } from 'react';
import Icono from './Iconos';
import { filtrarCatalogo } from '../presentacion';

/**
 * Listado del catálogo de propiedades con búsqueda y filtros por tipo y estado.
 *
 * Props:
 * - propiedades: lista de propiedades
 * - cargando / error: estado de la carga
 * - alEditar: abre el panel de edición
 * - alPedirEliminar: solicita la eliminación (la confirmación la maneja App)
 */

const TIPOS = ['Departamento', 'Casa', 'Terreno', 'Oficina'];

// Tono de la etiqueta según disponibilidad comercial
const TONO_ESTADO = {
  Disponible: 'exito',
  Reservada: 'alerta',
  Vendida: 'neutra',
  Arrendada: 'neutra',
  Retirada: 'neutra',
};

const ICONO_TIPO = {
  Departamento: 'edificio',
  Casa: 'casa',
  Terreno: 'etiqueta',
  Oficina: 'edificio',
};

function TablaPropiedades({ propiedades, cargando, error, alEditar, alPedirEliminar }) {
  const [busqueda, setBusqueda] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('Todos');
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroOperacion, setFiltroOperacion] = useState('Todas');

  if (cargando) {
    return <div className="state-message">Cargando catálogo...</div>;
  }

  if (error) {
    return (
      <div className="panel-cuerpo">
        <div className="alert-error">
          <Icono nombre="alerta" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  if (!propiedades || propiedades.length === 0) {
    return (
      <div className="state-message empty">
        <Icono nombre="edificio" tamano={20} />
        <span className="vacio-titulo">El catálogo está vacío</span>
        <span className="vacio-detalle">
          Carga las propiedades disponibles para poder asociarlas a los leads interesados.
        </span>
      </div>
    );
  }

  const filtradas = filtrarCatalogo(propiedades, {busqueda,tipo:filtroTipo,estado:filtroEstado,operacion:filtroOperacion});
  const limpiarFiltros = () => { setBusqueda(''); setFiltroTipo('Todos'); setFiltroEstado('Todos'); setFiltroOperacion('Todas'); };
  const hayFiltros = busqueda || filtroTipo !== 'Todos' || filtroEstado !== 'Todos' || filtroOperacion !== 'Todas';

  return (
    <>
      <div className="barra-herramientas">
        <div className="campo-busqueda">
          <Icono nombre="buscar" tamano={14} />
          <input
            type="search"
            className="search-input"
            placeholder="Título, comuna, dirección o código"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            aria-label="Buscar propiedades"
          />
        </div>

        <select
          className="filter-select"
          value={filtroTipo}
          aria-label="Filtrar propiedades por tipo"
          onChange={(e) => setFiltroTipo(e.target.value)}
        >
          <option value="Todos">Todos los tipos</option>
          {TIPOS.map((tipo) => (
            <option key={tipo} value={tipo}>
              {tipo}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={filtroEstado}
          aria-label="Filtrar propiedades por estado"
          onChange={(e) => setFiltroEstado(e.target.value)}
        >
          <option value="Todos">Todos los estados</option>
          <option value="Disponible">Disponible</option>
          <option value="Reservada">Reservada</option>
          <option value="Vendida">Vendida</option>
          <option value="Arrendada">Arrendada</option>
          <option value="Retirada">Retirada</option>
        </select>

        <select className="filter-select" value={filtroOperacion}
          aria-label="Filtrar propiedades por operación" onChange={(e) => setFiltroOperacion(e.target.value)}>
          <option value="Todas">Venta y arriendo</option>
          <option value="Compra">Venta</option>
          <option value="Arriendo">Arriendo</option>
        </select>
        {hayFiltros && <button className="btn-secondary" onClick={limpiarFiltros}>Limpiar filtros</button>}
        <span className="results-count" role="status">
          {filtradas.length} de {propiedades.length}
        </span>
      </div>

      {filtradas.length === 0 ? (
        <div className="state-message empty">
          <span className="vacio-titulo">Sin resultados</span>
          <span className="vacio-detalle">Ajusta la búsqueda o los filtros aplicados.</span>
        </div>
      ) : (
        <div className="table-wrapper" tabIndex={0} role="region" aria-label="Catálogo de propiedades; desplazamiento horizontal disponible">
          <table className="leads-table">
            <thead>
              <tr>
                <th>Propiedad</th>
                <th>Tipo</th>
                <th>Operación y distribución</th>
                <th>Precio</th>
                <th>Estado</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtradas.map((prop) => (
                <tr key={prop.id}>
                  <td>
                    <div className="celda-doble">
                      <span className="celda-principal">{prop.titulo}</span>
                      <span className="celda-secundaria">{prop.comuna || 'Comuna sin registrar'} · {prop.direccion}</span>
                      <details className="catalogo-detalle">
                        <summary>Ver ficha del inmueble</summary>
                        <FichaCatalogo propiedad={prop} />
                      </details>
                    </div>
                  </td>

                  <td>
                    <span className="etiqueta neutra">
                      <Icono nombre={ICONO_TIPO[prop.tipo] || 'edificio'} tamano={11} />
                      {prop.tipo}
                    </span>
                  </td>

                  <td>
                    <div className="celda-doble">
                      <span className="celda-principal">{prop.tipo_operacion === 'Compra' ? 'Venta' : prop.tipo_operacion || 'Sin definir'}</span>
                      <span className="celda-secundaria">{prop.dormitorios ?? '—'}D · {prop.banos ?? '—'}B</span>
                    </div>
                  </td>

                  <td className="col-numero">
                    {prop.precio ? `${prop.precio.toLocaleString('es-CL')} ${prop.moneda || ''}`.trim() : '—'}
                  </td>

                  <td>
                    <span className={`etiqueta ${TONO_ESTADO[prop.estado] || 'neutra'}`}>
                      {prop.estado}
                    </span>
                  </td>

                  <td className="col-acciones">
                    <div className="acciones-celda">
                      <button className="btn-icono" onClick={() => alEditar(prop)} title="Editar">
                        <Icono nombre="editar" />
                      </button>
                      <button
                        className="btn-icono peligro"
                        onClick={() => alPedirEliminar(prop)}
                        title="Eliminar"
                      >
                        <Icono nombre="eliminar" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default TablaPropiedades;

function FotoCatalogo({ url, titulo }) {
  const [fallo, setFallo] = useState(false);
  return fallo ? <span>Fotografía no disponible</span> : <img className="catalogo-foto" src={url} alt={titulo}
    loading="lazy" referrerPolicy="no-referrer" onError={() => setFallo(true)} />;
}

function FichaCatalogo({ propiedad: p }) {
  const fotos = p.fotografias || [];
  const ordenadas = p.foto_principal ? [p.foto_principal, ...fotos.filter(url => url !== p.foto_principal)] : fotos;
  return <div>
    <dl>
      {[['Código', p.codigo_interno], ['Superficie útil (m²)', p.superficie_util], ['Superficie total (m²)', p.superficie_total],
        ['Estacionamientos', p.estacionamientos], ['Bodega', p.bodega == null ? null : p.bodega ? 'Sí' : 'No'],
        ['Gastos comunes (CLP)', p.gastos_comunes], ['Disponibilidad desde', p.fecha_disponibilidad],
        ['Descripción', p.descripcion], ['Características', p.caracteristicas]].map(([etiqueta, valor]) =>
          <div key={etiqueta}><dt>{etiqueta}</dt><dd>{valor ?? 'Sin registrar'}</dd></div>)}
      {(p.propietario_nombre || p.propietario_email || p.propietario_telefono || p.captador) && <>
        <dt>Propietario (administración)</dt><dd>{p.propietario_nombre || 'Sin registrar'}</dd>
        <dt>Contacto</dt><dd>{[p.propietario_email, p.propietario_telefono].filter(Boolean).join(' · ') || 'Sin registrar'}</dd>
        <dt>Captador</dt><dd>{p.captador || 'Sin registrar'}</dd>
      </>}
    </dl>
    {ordenadas.length ? <div className="catalogo-galeria">{ordenadas.map((url, i) => <FotoCatalogo key={url} url={url} titulo={`${p.titulo}, fotografía ${i + 1}`} />)}</div> : <p>Sin fotografías registradas</p>}
  </div>;
}

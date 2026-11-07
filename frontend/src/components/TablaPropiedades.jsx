import React, { useState } from 'react';
import Icono from './Iconos';
import ListadoPaginado from './ListadoPaginado';
import Drawer from './Drawer';
import { filtrarCatalogo, fotoPrincipal, fotoReferencial } from '../presentacion';

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
  const [fichaId, setFichaId] = useState(null);

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
  const seleccionada = propiedades.find(propiedad => propiedad.id === fichaId);
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
        <ListadoPaginado key={JSON.stringify([busqueda,filtroTipo,filtroEstado,filtroOperacion])} items={filtradas} etiqueta="propiedades">{(visibles) => ( <div className="table-wrapper" tabIndex={0} role="region" aria-label="Catálogo de propiedades; desplazamiento horizontal disponible">
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
              {visibles.map((prop) => (
                <tr key={prop.id}>
                  <td>
                    <div className="catalogo-identidad">
                    <Miniatura propiedad={prop} />
                    <div className="celda-doble">
                      <span className="celda-principal">{prop.titulo}</span>
                      <span className="celda-secundaria">{prop.comuna || 'Comuna sin registrar'} · {prop.direccion}</span>
                      <button type="button" className="catalogo-abrir-ficha" onClick={() => setFichaId(prop.id)}>
                        Ver ficha del inmueble
                      </button>
                    </div>
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
        </div> )}</ListadoPaginado>
      )}
      <Drawer abierto={Boolean(seleccionada)} titulo={seleccionada?.titulo || 'Ficha del inmueble'}
        subtitulo="Ficha del inmueble" ancho alCerrar={() => setFichaId(null)}>
        {seleccionada && <FichaCatalogo propiedad={seleccionada} />}
      </Drawer>
    </>
  );
}

export default TablaPropiedades;

function Miniatura({ propiedad }) {
  const url = fotoPrincipal(propiedad);
  return url ? <figure className="catalogo-miniatura">
    <a href={url} target="_blank" rel="noopener noreferrer" aria-label={`Ampliar fotografía de ${propiedad.titulo}`}>
      <FotoCatalogo key={url} url={url} titulo={propiedad.titulo} />
    </a>
  </figure> : <div className="catalogo-sin-foto"><Icono nombre={ICONO_TIPO[propiedad.tipo] || 'edificio'} tamano={24} /><span>Sin foto</span></div>;
}

function FotoCatalogo({ url, titulo }) {
  const [fallo, setFallo] = useState(false);
  return fallo ? <span className="catalogo-sin-foto">Foto no disponible</span> : <img className="catalogo-foto" src={url} alt={`${fotoReferencial(url) ? 'Imagen referencial: ' : ''}${titulo}`}
    loading="lazy" decoding="async" referrerPolicy="no-referrer" onError={() => setFallo(true)} />;
}

function FichaCatalogo({ propiedad: p }) {
  const fotos = Array.isArray(p.fotografias) ? p.fotografias : [];
  const ordenadas = [...new Set([p.foto_principal, ...fotos])]
    .filter(url => fotoPrincipal({ foto_principal: url }));
  const numero = valor => valor == null ? 'Sin registrar' : valor.toLocaleString('es-CL');
  const datos = [
    ['Código interno', p.codigo_interno],
    ['Dormitorios', p.dormitorios], ['Baños', p.banos],
    ['Superficie útil', p.superficie_util == null ? null : `${numero(p.superficie_util)} m²`],
    ['Superficie total', p.superficie_total == null ? null : `${numero(p.superficie_total)} m²`],
    ['Estacionamientos', p.estacionamientos],
    ['Bodega', p.bodega == null ? null : p.bodega ? 'Sí' : 'No'],
    ['Gastos comunes', p.gastos_comunes == null ? null : `${numero(p.gastos_comunes)} CLP`],
    ['Disponible desde', p.fecha_disponibilidad ? p.fecha_disponibilidad.split('-').reverse().join('-') : null],
  ];
  const faltantes = datos.filter(([, valor]) => valor == null || valor === '').length;
  return <div className="inmueble-ficha">
    <section className="inmueble-resumen" aria-label="Información comercial">
      <span className={`etiqueta ${TONO_ESTADO[p.estado] || 'neutra'}`}>{p.estado}</span>
      <p className="inmueble-precio">{p.precio == null ? 'Precio sin registrar' : `${numero(p.precio)} ${p.moneda || '(moneda sin registrar)'}`}</p>
      <p>{p.tipo} · {p.tipo_operacion === 'Compra' ? 'Venta' : p.tipo_operacion || 'Operación sin registrar'}</p>
      <p>{[p.direccion, p.comuna].filter(Boolean).join(' · ') || 'Ubicación sin registrar'}</p>
    </section>
    <section className="inmueble-seccion" aria-labelledby={`datos-inmueble-${p.id}`}>
      <h3 id={`datos-inmueble-${p.id}`}>Datos del inmueble</h3>
      {faltantes > 0 && <p className="inmueble-pendientes">{faltantes} datos de esta sección pendientes de completar.</p>}
      <dl className="inmueble-datos">{datos.map(([etiqueta, valor]) =>
        <div key={etiqueta}><dt>{etiqueta}</dt><dd className={valor == null || valor === '' ? 'inmueble-sin-dato' : undefined}>{valor == null || valor === '' ? 'Sin registrar' : valor}</dd></div>)}
      </dl>
    </section>
    <section className="inmueble-seccion" aria-label="Descripción y características">
      <h3>Descripción</h3><p className="inmueble-texto">{p.descripcion || 'Sin descripción registrada.'}</p>
      <h3>Características</h3><p className="inmueble-texto">{p.caracteristicas || 'Sin características registradas.'}</p>
    </section>
    {(p.propietario_nombre || p.propietario_email || p.propietario_telefono || p.captador) &&
      <section className="inmueble-seccion" aria-label="Información administrativa">
        <h3>Administración</h3>
        <dl className="inmueble-datos">
          <div><dt>Propietario</dt><dd>{p.propietario_nombre || 'Sin registrar'}</dd></div>
          <div><dt>Captador</dt><dd>{p.captador || 'Sin registrar'}</dd></div>
          <div><dt>Correo</dt><dd>{p.propietario_email || 'Sin registrar'}</dd></div>
          <div><dt>Teléfono</dt><dd>{p.propietario_telefono || 'Sin registrar'}</dd></div>
        </dl>
      </section>}
    <section className="inmueble-seccion" aria-label="Fotografías del inmueble">
      <h3>Fotografías</h3>
      {ordenadas.length ? <div className="catalogo-galeria">{ordenadas.map((url, i) => <figure key={url}>
        <a href={url} target="_blank" rel="noopener noreferrer" aria-label={`Ampliar fotografía ${i + 1} de ${p.titulo}`}>
          <FotoCatalogo url={url} titulo={`${p.titulo}, fotografía ${i + 1}`} />
        </a>
      </figure>)}</div> : <p>Sin fotografías registradas.</p>}
    </section>
  </div>;
}

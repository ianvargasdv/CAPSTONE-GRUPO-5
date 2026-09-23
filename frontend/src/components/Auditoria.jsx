import React, { useCallback, useEffect, useState } from 'react';
import Icono from './Iconos';
import { obtenerAuditoria, obtenerFiltrosAuditoria } from '../api';

/**
 * Registro de actividad del sistema. Solo lo ve el rol admin.
 *
 * Responde a "quién cambió esto y cuándo", que es la pregunta que aparece cuando un
 * lead cambia de estado sin explicación o una propiedad desaparece del catálogo. En
 * una inmobiliaria con varios ejecutivos trabajando la misma cartera, sin esto no
 * hay forma de reconstruir lo que pasó.
 *
 * A diferencia del resto de las vistas, este componente pide sus propios datos en
 * lugar de recibirlos por props. El motivo es que la consulta depende de siete
 * filtros y de la página actual: mantener todo eso en App.jsx significaría subir
 * estado que solo esta vista usa. Las demás vistas reciben props porque sus datos se
 * comparten entre secciones; el registro de auditoría no se comparte con ninguna.
 */

const POR_PAGINA = 25;

// Sin filtros aplicados. Se usa también para el botón de limpiar.
const FILTROS_VACIOS = {
  busqueda: '',
  usuario_email: '',
  entidad: '',
  accion: '',
  desde: '',
  hasta: '',
};

// Los valores que guarda la base son en minúscula y sin tilde. Acá se traducen a
// algo presentable, sin tocar lo que está almacenado.
const ETIQUETA_ACCION = {
  crear: 'Creación',
  actualizar: 'Modificación',
  eliminar: 'Eliminación',
  generar: 'Generación',
};

const ETIQUETA_ENTIDAD = {
  lead: 'Lead',
  propiedad: 'Propiedad',
  tarea: 'Tarea',
  interaccion: 'Interacción',
  interes: 'Interés',
  analisis: 'Análisis de IA',
};

// El color comunica el riesgo de la acción: lo que se borra no se recupera
const TONO_ACCION = {
  crear: 'exito',
  actualizar: 'info',
  eliminar: 'peligro',
  generar: 'alerta',
};

/** Fecha y hora en formato local, que es como el usuario piensa el tiempo. */
function fechaHora(valor) {
  if (!valor) return '—';

  const fecha = new Date(valor);
  return fecha.toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function Auditoria() {
  const [filtros, setFiltros] = useState(FILTROS_VACIOS);
  const [pagina, setPagina] = useState(1);

  // Se separa del campo de texto para no disparar una petición por cada tecla
  const [busquedaAplicada, setBusquedaAplicada] = useState('');

  const [datos, setDatos] = useState(null);
  const [opciones, setOpciones] = useState({ entidades: [], acciones: [], usuarios: [] });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  // Las opciones de los selectores no cambian con los filtros, se piden una vez
  useEffect(() => {
    obtenerFiltrosAuditoria()
      .then(setOpciones)
      .catch(() => {
        // Sin las opciones la vista sigue siendo usable: los selectores quedan
        // vacíos pero el listado y la búsqueda por texto funcionan igual
      });
  }, []);

  const cargar = useCallback(async () => {
    try {
      setCargando(true);
      setError(null);
      setDatos(
        await obtenerAuditoria({
          ...filtros,
          busqueda: busquedaAplicada,
          pagina,
          por_pagina: POR_PAGINA,
        })
      );
    } catch (err) {
      setError(err.message || 'No se pudo cargar el registro de actividad.');
    } finally {
      setCargando(false);
    }
  }, [filtros, busquedaAplicada, pagina]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  // El texto se aplica cuando el usuario deja de escribir
  useEffect(() => {
    const espera = setTimeout(() => {
      setBusquedaAplicada(filtros.busqueda.trim());
      setPagina(1);
    }, 400);

    return () => clearTimeout(espera);
  }, [filtros.busqueda]);

  /**
   * Cambia un filtro y vuelve a la primera página.
   *
   * Sin el salto a la primera página se puede quedar mirando la página 4 de un
   * resultado que ahora tiene una sola, y la tabla aparecería vacía sin motivo
   * aparente.
   */
  const cambiarFiltro = (campo, valor) => {
    setFiltros((previos) => ({ ...previos, [campo]: valor }));
    if (campo !== 'busqueda') setPagina(1);
  };

  const limpiarFiltros = () => {
    setFiltros(FILTROS_VACIOS);
    setBusquedaAplicada('');
    setPagina(1);
  };

  const hayFiltros = Object.values(filtros).some((valor) => valor !== '');

  const total = datos?.total ?? 0;
  const totalPaginas = datos?.total_paginas ?? 0;
  const registros = datos?.registros ?? [];

  // Rango que se está viendo, para que el conteo signifique algo concreto
  const desdeFila = total === 0 ? 0 : (pagina - 1) * POR_PAGINA + 1;
  const hastaFila = Math.min(pagina * POR_PAGINA, total);

  return (
    <div className="panel">
      <div className="barra-herramientas">
        <div className="campo-busqueda">
          <Icono nombre="buscar" tamano={14} />
          <input
            type="text"
            className="search-input"
            placeholder="Buscar en la descripción..."
            value={filtros.busqueda}
            onChange={(e) => cambiarFiltro('busqueda', e.target.value)}
            aria-label="Buscar en el registro de actividad"
          />
        </div>

        <select
          className="filter-select"
          value={filtros.usuario_email}
          onChange={(e) => cambiarFiltro('usuario_email', e.target.value)}
          aria-label="Filtrar por usuario"
        >
          <option value="">Todos los usuarios</option>
          {opciones.usuarios.map((correo) => (
            <option key={correo} value={correo}>
              {correo}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={filtros.entidad}
          onChange={(e) => cambiarFiltro('entidad', e.target.value)}
          aria-label="Filtrar por tipo de registro"
        >
          <option value="">Todo el sistema</option>
          {opciones.entidades.map((valor) => (
            <option key={valor} value={valor}>
              {ETIQUETA_ENTIDAD[valor] || valor}
            </option>
          ))}
        </select>

        <select
          className="filter-select"
          value={filtros.accion}
          onChange={(e) => cambiarFiltro('accion', e.target.value)}
          aria-label="Filtrar por tipo de acción"
        >
          <option value="">Toda acción</option>
          {opciones.acciones.map((valor) => (
            <option key={valor} value={valor}>
              {ETIQUETA_ACCION[valor] || valor}
            </option>
          ))}
        </select>

        <div className="rango-fechas">
          <input
            type="date"
            className="filter-select"
            value={filtros.desde}
            max={filtros.hasta || undefined}
            onChange={(e) => cambiarFiltro('desde', e.target.value)}
            aria-label="Desde la fecha"
          />
          <span className="rango-separador">a</span>
          <input
            type="date"
            className="filter-select"
            value={filtros.hasta}
            min={filtros.desde || undefined}
            onChange={(e) => cambiarFiltro('hasta', e.target.value)}
            aria-label="Hasta la fecha"
          />
        </div>

        {hayFiltros && (
          <button className="btn-secondary" onClick={limpiarFiltros}>
            <Icono nombre="cerrar" tamano={13} />
            Limpiar
          </button>
        )}

        <span className="results-count">
          {cargando
            ? 'Cargando...'
            : total === 0
              ? 'Sin registros'
              : `${desdeFila}–${hastaFila} de ${total.toLocaleString('es-CL')}`}
        </span>
      </div>

      {error && (
        <div className="panel-cuerpo">
          <div className="alert-error">
            <Icono nombre="alerta" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {!error && cargando && !datos && (
        <div className="state-message">Cargando el registro de actividad...</div>
      )}

      {!error && datos && total === 0 && (
        <div className="state-message empty">
          <Icono nombre="historial" tamano={20} />
          <span className="vacio-titulo">
            {hayFiltros ? 'Ningún registro coincide con los filtros' : 'Todavía no hay actividad registrada'}
          </span>
          <span className="vacio-detalle">
            {hayFiltros
              ? 'Prueba con un rango de fechas más amplio o quita algún filtro.'
              : 'Cada vez que alguien cree, modifique o elimine un registro va a quedar anotado acá.'}
          </span>
        </div>
      )}

      {!error && registros.length > 0 && (
        <>
          <div className="table-wrapper">
            <table className="leads-table tabla-auditoria">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Tipo</th>
                  <th>Qué pasó</th>
                  <th>Detalle</th>
                </tr>
              </thead>
              <tbody>
                {registros.map((registro) => (
                  <tr key={registro.id}>
                    <td className="col-fecha">{fechaHora(registro.fecha_creacion)}</td>
                    <td>
                      {/* El correo se guarda junto al registro, así que sigue
                          apareciendo aunque la cuenta se haya dado de baja */}
                      {registro.usuario_email || <span className="texto-suave">sin usuario</span>}
                    </td>
                    <td>
                      <span className={`etiqueta ${TONO_ACCION[registro.accion] || 'neutra'}`}>
                        {ETIQUETA_ACCION[registro.accion] || registro.accion}
                      </span>
                    </td>
                    <td>
                      {ETIQUETA_ENTIDAD[registro.entidad] || registro.entidad}
                      {registro.entidad_id != null && (
                        <span className="texto-suave"> #{registro.entidad_id}</span>
                      )}
                    </td>
                    <td className="celda-principal celda-descripcion">
                      {registro.descripcion || '—'}
                    </td>
                    <td className="celda-detalle">
                      {registro.detalle ? (
                        <code>{registro.detalle}</code>
                      ) : (
                        <span className="texto-suave">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPaginas > 1 && (
            <div className="paginacion">
              <button
                className="btn-secondary"
                onClick={() => setPagina((p) => p - 1)}
                disabled={pagina <= 1 || cargando}
              >
                Anterior
              </button>

              <span className="paginacion-texto">
                Página {pagina} de {totalPaginas}
              </span>

              <button
                className="btn-secondary"
                onClick={() => setPagina((p) => p + 1)}
                disabled={pagina >= totalPaginas || cargando}
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Auditoria;

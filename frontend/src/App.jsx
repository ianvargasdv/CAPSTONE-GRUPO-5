import React, { useEffect, useRef, useState } from 'react';
import {
  obtenerLeads,
  crearLead,
  actualizarLead,
  eliminarLead,
  obtenerPropiedades,
  crearPropiedad,
  actualizarPropiedad,
  eliminarPropiedad,
  obtenerInteracciones,
  crearInteraccion,
  obtenerTareas,
  crearTarea,
  actualizarTarea,
  eliminarTarea,
  obtenerIntereses,
  crearInteres,
  eliminarInteres,
  iniciarSesion,
  obtenerPerfil,
  obtenerToken,
  borrarToken,
  registrarCierreDeSesion,
} from './api';

import Icono from './components/Iconos';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import Drawer from './components/Drawer';
import Confirmacion from './components/Confirmacion';
import Dashboard from './components/Dashboard';
import TablaLeads from './components/TablaLeads';
import TablaPropiedades from './components/TablaPropiedades';
import TablaTareas from './components/TablaTareas';
import FormularioLead from './components/FormularioLead';
import FormularioPropiedad from './components/FormularioPropiedad';
import FormularioTarea from './components/FormularioTarea';
import FormularioInteraccion from './components/FormularioInteraccion';
import PropiedadesInteres from './components/PropiedadesInteres';
import HistorialInteracciones from './components/HistorialInteracciones';

/** Configuración de cada vista: título de la barra superior y su acción principal. */
const VISTAS = {
  inicio: { titulo: 'Inicio', subtitulo: 'Resumen de la operación' },
  leads: { titulo: 'Leads', accion: 'Nuevo lead', entidad: 'lead' },
  propiedades: { titulo: 'Propiedades', accion: 'Nueva propiedad', entidad: 'propiedad' },
  tareas: { titulo: 'Tareas', accion: 'Nueva tarea', entidad: 'tarea' },
};

/** Título del panel lateral según la entidad y si se está creando o editando. */
const TITULOS_PANEL = {
  lead: { crear: 'Nuevo lead', editar: 'Editar lead' },
  propiedad: { crear: 'Nueva propiedad', editar: 'Editar propiedad' },
  tarea: { crear: 'Nueva tarea', editar: 'Editar tarea' },
};

/** Tono de la etiqueta según el nivel de atención que requiere el lead. */
const TONO_CATEGORIA = {
  Urgente: 'peligro',
  Alta: 'alerta',
  Normal: 'neutra',
  Baja: 'neutra',
  'Sin acción': 'neutra',
};

/** Texto del modal de confirmación para cada tipo de registro. */
const TEXTOS_ELIMINAR = {
  lead: (r) => ({
    titulo: 'Eliminar lead',
    mensaje: `Se eliminará a ${r.nombre} junto con su historial de interacciones y sus propiedades de interés. Esta acción no se puede deshacer.`,
  }),
  propiedad: (r) => ({
    titulo: 'Eliminar propiedad',
    mensaje: `Se eliminará "${r.titulo}" del catálogo. Esta acción no se puede deshacer.`,
  }),
  tarea: (r) => ({
    titulo: 'Eliminar tarea',
    mensaje: `Se eliminará la tarea "${r.titulo}". Esta acción no se puede deshacer.`,
  }),
};

function App() {
  const [vista, setVista] = useState('inicio');
  const [toast, setToast] = useState(null);
  const temporizadorToast = useRef(null);

  // ── Sesión ──
  // usuario en null significa que no hay sesión y se muestra el login.
  // verificandoSesion evita que aparezca el login por un instante mientras se
  // comprueba si el token guardado sigue siendo válido.
  const [usuario, setUsuario] = useState(null);
  const [verificandoSesion, setVerificandoSesion] = useState(true);
  // Explica en la pantalla de acceso por qué se cerró la sesión sola
  const [avisoSesion, setAvisoSesion] = useState(null);

  /**
   * Muestra un aviso breve. Cancela el temporizador anterior para que dos avisos
   * seguidos no se corten entre sí.
   */
  const mostrarToast = (mensaje) => {
    if (temporizadorToast.current) clearTimeout(temporizadorToast.current);
    setToast(mensaje);
    temporizadorToast.current = setTimeout(() => setToast(null), 3000);
  };

  // Evita que quede un temporizador pendiente si el componente se desmonta
  useEffect(() => () => clearTimeout(temporizadorToast.current), []);

  // ── Datos ──
  const [leads, setLeads] = useState([]);
  const [cargandoLeads, setCargandoLeads] = useState(true);
  const [errorLeads, setErrorLeads] = useState(null);

  const [propiedades, setPropiedades] = useState([]);
  const [cargandoPropiedades, setCargandoPropiedades] = useState(true);
  const [errorPropiedades, setErrorPropiedades] = useState(null);

  const [tareas, setTareas] = useState([]);
  const [cargandoTareas, setCargandoTareas] = useState(true);
  const [errorTareas, setErrorTareas] = useState(null);

  // ── Panel lateral de formularios: { entidad, registro } o null ──
  const [panelForm, setPanelForm] = useState(null);

  // ── Ficha del lead y sus datos asociados ──
  const [fichaLead, setFichaLead] = useState(null);
  const [interacciones, setInteracciones] = useState([]);
  const [cargandoInteracciones, setCargandoInteracciones] = useState(false);
  const [errorInteracciones, setErrorInteracciones] = useState(null);
  const [intereses, setIntereses] = useState([]);
  const [cargandoIntereses, setCargandoIntereses] = useState(false);
  const [errorIntereses, setErrorIntereses] = useState(null);

  // ── Confirmación de borrado: { entidad, registro } o null ──
  const [confirmacion, setConfirmacion] = useState(null);
  const [eliminando, setEliminando] = useState(false);

  // ══════════ Carga inicial ══════════

  const cargarLeads = async () => {
    try {
      setCargandoLeads(true);
      setErrorLeads(null);
      setLeads(await obtenerLeads());
    } catch {
      setErrorLeads('No se pudo conectar con el backend para cargar los leads.');
    } finally {
      setCargandoLeads(false);
    }
  };

  const cargarPropiedades = async () => {
    try {
      setCargandoPropiedades(true);
      setErrorPropiedades(null);
      setPropiedades(await obtenerPropiedades());
    } catch {
      setErrorPropiedades('No se pudo conectar con el backend para cargar las propiedades.');
    } finally {
      setCargandoPropiedades(false);
    }
  };

  const cargarTareas = async () => {
    try {
      setCargandoTareas(true);
      setErrorTareas(null);
      setTareas(await obtenerTareas());
    } catch {
      setErrorTareas('No se pudo conectar con el backend para cargar las tareas.');
    } finally {
      setCargandoTareas(false);
    }
  };

  // Los datos se piden solo cuando hay sesión: sin token la API responde 401
  useEffect(() => {
    if (!usuario) return;
    cargarLeads();
    cargarPropiedades();
    cargarTareas();
  }, [usuario]);

  // ══════════ Sesión ══════════

  /** Descarta los datos en memoria para que no queden a la vista del próximo usuario. */
  const limpiarDatos = () => {
    setLeads([]);
    setPropiedades([]);
    setTareas([]);
    setCargandoLeads(true);
    setCargandoPropiedades(true);
    setCargandoTareas(true);
    setPanelForm(null);
    setConfirmacion(null);
    setFichaLead(null);
    setInteracciones([]);
    setIntereses([]);
    setVista('inicio');
  };

  /** Salida voluntaria: no corresponde mostrar ningún aviso. */
  const cerrarSesion = () => {
    borrarToken();
    setUsuario(null);
    setAvisoSesion(null);
    limpiarDatos();
  };

  const manejarLogin = async (email, password) => {
    // Si falla, el error se propaga y lo muestra la pantalla de login
    const autenticado = await iniciarSesion(email, password);
    setAvisoSesion(null);
    setUsuario(autenticado);
  };

  useEffect(() => {
    // La capa de API avisa por aquí cuando el backend rechaza el token
    registrarCierreDeSesion(() => {
      setUsuario(null);
      setAvisoSesion('Tu sesión expiró. Vuelve a ingresar para continuar.');
      limpiarDatos();
    });

    // Al cargar la página se valida el token guardado contra el backend
    const validarSesionGuardada = async () => {
      if (!obtenerToken()) {
        setVerificandoSesion(false);
        return;
      }

      try {
        setUsuario(await obtenerPerfil());
      } catch {
        // Token vencido o inválido: se queda sin sesión y aparece el login
        borrarToken();
      } finally {
        setVerificandoSesion(false);
      }
    };

    validarSesionGuardada();
  }, []);

  // ══════════ Panel lateral ══════════

  const abrirCrear = (entidad) => setPanelForm({ entidad, registro: null });
  const abrirEditar = (entidad, registro) => setPanelForm({ entidad, registro });
  const cerrarPanelForm = () => setPanelForm(null);

  // ══════════ Ficha del lead ══════════

  const abrirFicha = async (lead) => {
    setFichaLead(lead);
    setInteracciones([]);
    setIntereses([]);
    setCargandoInteracciones(true);
    setCargandoIntereses(true);
    setErrorInteracciones(null);
    setErrorIntereses(null);

    try {
      setInteracciones(await obtenerInteracciones(lead.id));
    } catch {
      setErrorInteracciones('No se pudo cargar el historial de interacciones.');
    } finally {
      setCargandoInteracciones(false);
    }

    try {
      setIntereses(await obtenerIntereses(lead.id));
    } catch {
      setErrorIntereses('No se pudieron cargar las propiedades de interés.');
    } finally {
      setCargandoIntereses(false);
    }
  };

  const cerrarFicha = () => {
    setFichaLead(null);
    setInteracciones([]);
    setIntereses([]);
  };

  /** Desde la ficha se cierra el panel y se abre el de edición, para no apilar paneles. */
  const editarDesdeFicha = (lead) => {
    cerrarFicha();
    abrirEditar('lead', lead);
  };

  // ══════════ Leads ══════════

  /**
   * Reordena la lista igual que el backend: mayor prioridad primero.
   * Hace falta porque al crear o modificar un lead cambia su puntaje, y si solo
   * se reemplazara en su posición actual el listado dejaría de estar ordenado.
   */
  const ordenarPorPrioridad = (lista) =>
    [...lista].sort((a, b) => (b.puntaje ?? 0) - (a.puntaje ?? 0));

  /**
   * Vuelve a pedir los leads sin mostrar el estado de carga.
   *
   * Se usa después de registrar actividad (una interacción o una propiedad de
   * interés), porque la prioridad se calcula en el backend a partir de esa
   * actividad: sin esto el listado seguiría mostrando el puntaje anterior.
   */
  const refrescarLeads = async () => {
    try {
      const datos = await obtenerLeads();
      setLeads(datos);
      // Si la ficha está abierta, se reemplaza por la versión recalculada
      setFichaLead((actual) =>
        actual ? datos.find((l) => l.id === actual.id) ?? actual : actual
      );
    } catch {
      // Si falla se conservan los datos en pantalla: no vale interrumpir al usuario
    }
  };

  const guardarLead = async (datos) => {
    const editando = panelForm?.registro;

    if (editando) {
      const actualizado = await actualizarLead(editando.id, datos);
      setLeads((prev) => ordenarPorPrioridad(prev.map((l) => (l.id === actualizado.id ? actualizado : l))));
      if (fichaLead?.id === actualizado.id) setFichaLead(actualizado);
      mostrarToast('Lead actualizado');
    } else {
      const creado = await crearLead(datos);
      setLeads((prev) => ordenarPorPrioridad([...prev, creado]));
      mostrarToast('Lead registrado');
    }

    cerrarPanelForm();
  };

  /** Cambio rápido de estado desde la tabla, sin abrir el formulario. */
  const cambiarEstadoLead = async (lead, nuevoEstado) => {
    try {
      const actualizado = await actualizarLead(lead.id, { estado: nuevoEstado });
      setLeads((prev) => ordenarPorPrioridad(prev.map((l) => (l.id === actualizado.id ? actualizado : l))));
      if (fichaLead?.id === actualizado.id) setFichaLead(actualizado);
      mostrarToast(`${actualizado.nombre} ahora está en "${nuevoEstado}"`);
    } catch {
      mostrarToast('No se pudo cambiar el estado');
    }
  };

  // ══════════ Propiedades ══════════

  const guardarPropiedad = async (datos) => {
    const editando = panelForm?.registro;

    if (editando) {
      const actualizada = await actualizarPropiedad(editando.id, datos);
      setPropiedades((prev) => prev.map((p) => (p.id === actualizada.id ? actualizada : p)));
      mostrarToast('Propiedad actualizada');
    } else {
      const creada = await crearPropiedad(datos);
      setPropiedades((prev) => [...prev, creada]);
      mostrarToast('Propiedad registrada');
    }

    cerrarPanelForm();
  };

  // ══════════ Tareas ══════════

  const guardarTarea = async (datos) => {
    const editando = panelForm?.registro;

    if (editando) {
      const actualizada = await actualizarTarea(editando.id, datos);
      setTareas((prev) => prev.map((t) => (t.id === actualizada.id ? actualizada : t)));
      mostrarToast('Tarea actualizada');
    } else {
      const creada = await crearTarea(datos);
      setTareas((prev) => [creada, ...prev]);
      mostrarToast('Tarea creada');
    }

    cerrarPanelForm();
  };

  const completarTarea = async (tarea) => {
    try {
      const actualizada = await actualizarTarea(tarea.id, { estado: 'Completada' });
      setTareas((prev) => prev.map((t) => (t.id === actualizada.id ? actualizada : t)));
      mostrarToast('Tarea completada');
    } catch {
      mostrarToast('No se pudo completar la tarea');
    }
  };

  // ══════════ Interacciones y propiedades de interés ══════════

  // Registrar actividad cambia la prioridad del lead, por eso las tres funciones
  // piden los leads de nuevo al terminar.

  const guardarInteraccion = async (datos) => {
    const nueva = await crearInteraccion(fichaLead.id, datos);
    setInteracciones((prev) => [nueva, ...prev]);
    mostrarToast('Interacción registrada');
    refrescarLeads();
  };

  const guardarInteres = async (datos) => {
    const nuevo = await crearInteres(fichaLead.id, datos);
    setIntereses((prev) => [nuevo, ...prev]);
    mostrarToast('Propiedad asociada');
    refrescarLeads();
  };

  const quitarInteres = async (id) => {
    try {
      await eliminarInteres(id);
      setIntereses((prev) => prev.filter((i) => i.id !== id));
      mostrarToast('Propiedad desasociada');
      refrescarLeads();
    } catch {
      mostrarToast('No se pudo quitar la propiedad');
    }
  };

  // ══════════ Eliminación con confirmación ══════════

  const pedirEliminar = (entidad, registro) => setConfirmacion({ entidad, registro });

  const confirmarEliminar = async () => {
    const { entidad, registro } = confirmacion;

    try {
      setEliminando(true);

      if (entidad === 'lead') {
        await eliminarLead(registro.id);
        setLeads((prev) => prev.filter((l) => l.id !== registro.id));
        // Las tareas del lead quedan sin vínculo en la base; se refleja recargándolas
        setTareas((prev) =>
          prev.map((t) => (t.lead_id === registro.id ? { ...t, lead_id: null } : t))
        );
        if (fichaLead?.id === registro.id) cerrarFicha();
        mostrarToast('Lead eliminado');
      } else if (entidad === 'propiedad') {
        await eliminarPropiedad(registro.id);
        setPropiedades((prev) => prev.filter((p) => p.id !== registro.id));
        setIntereses((prev) => prev.filter((i) => i.propiedad_id !== registro.id));
        mostrarToast('Propiedad eliminada');
      } else if (entidad === 'tarea') {
        await eliminarTarea(registro.id);
        setTareas((prev) => prev.filter((t) => t.id !== registro.id));
        mostrarToast('Tarea eliminada');
      }

      setConfirmacion(null);
    } catch {
      mostrarToast('No se pudo eliminar el registro');
    } finally {
      setEliminando(false);
    }
  };

  // ══════════ Valores derivados ══════════

  const tareasAbiertas = tareas.filter((t) => t.estado !== 'Completada').length;
  const cargandoTodo = cargandoLeads || cargandoPropiedades || cargandoTareas;
  const configVista = VISTAS[vista];
  const textoConfirmacion = confirmacion
    ? TEXTOS_ELIMINAR[confirmacion.entidad](confirmacion.registro)
    : null;

  // Mientras se comprueba el token guardado no se muestra ni el login ni el CRM,
  // para evitar que la pantalla de acceso aparezca y desaparezca
  if (verificandoSesion) {
    return <div className="verificando-sesion">Verificando sesión...</div>;
  }

  if (!usuario) {
    return <Login alIniciarSesion={manejarLogin} aviso={avisoSesion} />;
  }

  return (
    <div className="app">
      <Sidebar
        vistaActiva={vista}
        alCambiarVista={setVista}
        contadores={{
          leads: leads.length,
          propiedades: propiedades.length,
          tareasPendientes: tareasAbiertas,
        }}
        usuario={usuario}
        alCerrarSesion={cerrarSesion}
      />

      <div className="area-trabajo">
        <header className="barra-superior">
          <div>
            <span className="titulo-pagina">{configVista.titulo}</span>
            {configVista.subtitulo && (
              <span className="subtitulo-pagina">{configVista.subtitulo}</span>
            )}
          </div>

          {configVista.accion && (
            <div className="acciones-barra">
              <button className="btn-primary" onClick={() => abrirCrear(configVista.entidad)}>
                <Icono nombre="mas" tamano={14} />
                {configVista.accion}
              </button>
            </div>
          )}
        </header>

        <main className="cuerpo-pagina">
          {vista === 'inicio' && (
            <Dashboard
              leads={leads}
              propiedades={propiedades}
              tareas={tareas}
              cargando={cargandoTodo}
              alVerFicha={abrirFicha}
              alEditarTarea={(tarea) => abrirEditar('tarea', tarea)}
              alIrA={setVista}
            />
          )}

          {vista === 'leads' && (
            <div className="panel">
              <TablaLeads
                leads={leads}
                tareas={tareas}
                cargando={cargandoLeads}
                error={errorLeads}
                alVerFicha={abrirFicha}
                alEditar={(lead) => abrirEditar('lead', lead)}
                alPedirEliminar={(lead) => pedirEliminar('lead', lead)}
                alCambiarEstado={cambiarEstadoLead}
              />
            </div>
          )}

          {vista === 'propiedades' && (
            <div className="panel">
              <TablaPropiedades
                propiedades={propiedades}
                cargando={cargandoPropiedades}
                error={errorPropiedades}
                alEditar={(prop) => abrirEditar('propiedad', prop)}
                alPedirEliminar={(prop) => pedirEliminar('propiedad', prop)}
              />
            </div>
          )}

          {vista === 'tareas' && (
            <div className="panel">
              <TablaTareas
                tareas={tareas}
                leads={leads}
                cargando={cargandoTareas}
                error={errorTareas}
                alEditar={(tarea) => abrirEditar('tarea', tarea)}
                alPedirEliminar={(tarea) => pedirEliminar('tarea', tarea)}
                alCompletar={completarTarea}
              />
            </div>
          )}
        </main>
      </div>

      {/* ── Panel lateral de creación y edición ── */}
      <Drawer
        abierto={Boolean(panelForm)}
        titulo={
          panelForm
            ? TITULOS_PANEL[panelForm.entidad][panelForm.registro ? 'editar' : 'crear']
            : ''
        }
        alCerrar={cerrarPanelForm}
      >
        {panelForm?.entidad === 'lead' && (
          <FormularioLead
            alGuardar={guardarLead}
            leadEditar={panelForm.registro}
            alCancelar={cerrarPanelForm}
          />
        )}

        {panelForm?.entidad === 'propiedad' && (
          <FormularioPropiedad
            alGuardar={guardarPropiedad}
            propiedadEditar={panelForm.registro}
            alCancelar={cerrarPanelForm}
          />
        )}

        {panelForm?.entidad === 'tarea' && (
          <FormularioTarea
            alGuardar={guardarTarea}
            tareaEditar={panelForm.registro}
            alCancelar={cerrarPanelForm}
            leads={leads}
          />
        )}
      </Drawer>

      {/* ── Ficha completa del lead ── */}
      <Drawer
        abierto={Boolean(fichaLead)}
        titulo={fichaLead?.nombre || ''}
        subtitulo={fichaLead ? `Lead #${fichaLead.id}` : ''}
        ancho
        alCerrar={cerrarFicha}
      >
        {fichaLead && (
          <>
            <div className="ficha-resumen">
              <div className="ficha-dato">
                <span className="ficha-dato-label">Correo</span>
                <span className="ficha-dato-valor">
                  <Icono nombre="correo" tamano={13} />
                  <span>{fichaLead.email}</span>
                </span>
              </div>

              <div className="ficha-dato">
                <span className="ficha-dato-label">Teléfono</span>
                <span className="ficha-dato-valor">
                  <Icono nombre="telefono" tamano={13} />
                  <span>{fichaLead.telefono || 'No registrado'}</span>
                </span>
              </div>

              <div className="ficha-dato">
                <span className="ficha-dato-label">Estado</span>
                <span className="ficha-dato-valor">
                  <span className="etiqueta neutra">{fichaLead.estado}</span>
                </span>
              </div>

              <div className="ficha-dato">
                <span className="ficha-dato-label">Prioridad</span>
                <span className="ficha-dato-valor">
                  <span
                    className={`prioridad prioridad-${(fichaLead.prioridad || 'media').toLowerCase()}`}
                  >
                    <span className="prioridad-punto" />
                    {fichaLead.prioridad}
                  </span>
                </span>
              </div>

              <div className="ficha-dato">
                <span className="ficha-dato-label">Registrado</span>
                <span className="ficha-dato-valor">
                  <Icono nombre="calendario" tamano={13} />
                  <span>
                    {fichaLead.fecha_creacion
                      ? new Date(fichaLead.fecha_creacion).toLocaleDateString('es-CL')
                      : '—'}
                  </span>
                </span>
              </div>

              <div className="ficha-dato">
                <span className="ficha-dato-label">Acciones</span>
                <button className="btn-secondary" onClick={() => editarDesdeFicha(fichaLead)}>
                  <Icono nombre="editar" tamano={13} />
                  Editar datos
                </button>
              </div>
            </div>

            {/* Explica de dónde sale el puntaje, para que la priorización no sea
                una caja negra y se pueda discutir el criterio */}
            {fichaLead.categoria && (
              <div className="ficha-seccion">
                <div className="ficha-seccion-encabezado">
                  <span className="ficha-seccion-titulo">Prioridad de atención</span>
                  <span className={`etiqueta ${TONO_CATEGORIA[fichaLead.categoria] || 'neutra'}`}>
                    {fichaLead.categoria}
                  </span>
                </div>

                <div className="bloque-prioridad">
                  <div className="prioridad-puntaje">
                    <span className="puntaje-numero">{fichaLead.puntaje}</span>
                    <span className="puntaje-label">puntos</span>
                  </div>

                  <ul className="lista-motivos">
                    {(fichaLead.motivos || []).map((motivo, indice) => (
                      <li key={indice}>{motivo}</li>
                    ))}
                  </ul>
                </div>

                <p className="nota-prioridad">
                  El puntaje se calcula con reglas sobre la actividad registrada:
                  antigüedad del último contacto, propiedades de interés, etapa del
                  embudo y prioridad asignada.
                </p>
              </div>
            )}

            <div className="ficha-seccion">
              <PropiedadesInteres
                intereses={intereses}
                propiedades={propiedades}
                cargando={cargandoIntereses}
                error={errorIntereses}
                alGuardar={guardarInteres}
                alEliminar={quitarInteres}
              />
            </div>

            <div className="ficha-seccion">
              <div className="ficha-seccion-encabezado">
                <span className="ficha-seccion-titulo">
                  Historial de contacto {interacciones.length > 0 && `(${interacciones.length})`}
                </span>
              </div>

              <FormularioInteraccion alGuardar={guardarInteraccion} />

              <div style={{ marginTop: '1.25rem' }}>
                <HistorialInteracciones
                  interacciones={interacciones}
                  cargando={cargandoInteracciones}
                  error={errorInteracciones}
                />
              </div>
            </div>
          </>
        )}
      </Drawer>

      {/* ── Confirmación de borrado ── */}
      <Confirmacion
        abierto={Boolean(confirmacion)}
        titulo={textoConfirmacion?.titulo || ''}
        mensaje={textoConfirmacion?.mensaje || ''}
        procesando={eliminando}
        alConfirmar={confirmarEliminar}
        alCancelar={() => setConfirmacion(null)}
      />

      {toast && (
        <div className="toast-notification">
          <Icono nombre="check" tamano={14} />
          {toast}
        </div>
      )}
    </div>
  );
}

export default App;

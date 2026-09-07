import React, { useEffect, useState } from 'react';
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
} from './api';
import FormularioLead from './components/FormularioLead';
import TablaLeads from './components/TablaLeads';
import FormularioPropiedad from './components/FormularioPropiedad';
import TablaPropiedades from './components/TablaPropiedades';
import FormularioInteraccion from './components/FormularioInteraccion';
import HistorialInteracciones from './components/HistorialInteracciones';
import FormularioTarea from './components/FormularioTarea';
import TablaTareas from './components/TablaTareas';

function App() {
  const [pestañaActiva, setPestañaActiva] = useState('leads');

  // Estado del toast
  const [toast, setToast] = useState(null);

  const mostrarToast = (mensaje) => {
    setToast(mensaje);
    setTimeout(() => setToast(null), 3000);
  };

  // --- Estado de Leads ---
  const [leads, setLeads] = useState([]);
  const [cargandoLeads, setCargandoLeads] = useState(true);
  const [errorLeads, setErrorLeads] = useState(null);
  const [leadEditar, setLeadEditar] = useState(null);

  // --- Estado de Propiedades ---
  const [propiedades, setPropiedades] = useState([]);
  const [cargandoPropiedades, setCargandoPropiedades] = useState(true);
  const [errorPropiedades, setErrorPropiedades] = useState(null);
  const [propiedadEditar, setPropiedadEditar] = useState(null);

  // --- Estado del panel de Interacciones ---
  const [leadSeleccionado, setLeadSeleccionado] = useState(null);
  const [interacciones, setInteracciones] = useState([]);
  const [cargandoInteracciones, setCargandoInteracciones] = useState(false);
  const [errorInteracciones, setErrorInteracciones] = useState(null);

  // --- Estado de Tareas ---
  const [tareas, setTareas] = useState([]);
  const [cargandoTareas, setCargandoTareas] = useState(true);
  const [errorTareas, setErrorTareas] = useState(null);
  const [tareaEditar, setTareaEditar] = useState(null);

  // Carga inicial de todas las entidades
  const cargarLeads = async () => {
    try {
      setCargandoLeads(true);
      setErrorLeads(null);
      const datos = await obtenerLeads();
      setLeads(datos);
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
      const datos = await obtenerPropiedades();
      setPropiedades(datos);
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
      const datos = await obtenerTareas();
      setTareas(datos);
    } catch {
      setErrorTareas('No se pudo conectar con el backend para cargar las tareas.');
    } finally {
      setCargandoTareas(false);
    }
  };

  useEffect(() => {
    cargarLeads();
    cargarPropiedades();
    cargarTareas();
  }, []);

  // --- Handlers de Leads ---

  const manejarGuardarLead = async (datosLead) => {
    if (leadEditar) {
      const leadActualizado = await actualizarLead(leadEditar.id, datosLead);
      setLeads((prev) => prev.map((l) => (l.id === leadActualizado.id ? leadActualizado : l)));
      setLeadEditar(null);
      mostrarToast('Lead actualizado con éxito ✓');
    } else {
      const leadGuardado = await crearLead(datosLead);
      setLeads((prev) => [...prev, leadGuardado]);
      mostrarToast('Lead registrado con éxito en Supabase ✓');
    }
  };

  const manejarEditarLead = (lead) => {
    setLeadEditar(lead);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const manejarEliminarLead = async (id) => {
    await eliminarLead(id);
    setLeads((prev) => prev.filter((l) => l.id !== id));
    if (leadSeleccionado?.id === id) {
      setLeadSeleccionado(null);
      setInteracciones([]);
    }
    mostrarToast('Lead eliminado ✓');
  };

  const manejarCancelarEdicionLead = () => setLeadEditar(null);

  // --- Handlers de Propiedades ---

  const manejarGuardarPropiedad = async (datosPropiedad) => {
    if (propiedadEditar) {
      const propiedadActualizada = await actualizarPropiedad(propiedadEditar.id, datosPropiedad);
      setPropiedades((prev) =>
        prev.map((p) => (p.id === propiedadActualizada.id ? propiedadActualizada : p))
      );
      setPropiedadEditar(null);
      mostrarToast('Propiedad actualizada con éxito ✓');
    } else {
      const propiedadGuardada = await crearPropiedad(datosPropiedad);
      setPropiedades((prev) => [...prev, propiedadGuardada]);
      mostrarToast('Propiedad registrada con éxito en Supabase ✓');
    }
  };

  const manejarEditarPropiedad = (propiedad) => {
    setPropiedadEditar(propiedad);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const manejarEliminarPropiedad = async (id) => {
    await eliminarPropiedad(id);
    setPropiedades((prev) => prev.filter((p) => p.id !== id));
    mostrarToast('Propiedad eliminada ✓');
  };

  const manejarCancelarEdicionPropiedad = () => setPropiedadEditar(null);

  // --- Handlers de Interacciones ---

  const manejarVerHistorial = async (lead) => {
    if (leadSeleccionado?.id === lead.id) {
      setLeadSeleccionado(null);
      setInteracciones([]);
      return;
    }
    setLeadSeleccionado(lead);
    setInteracciones([]);
    setCargandoInteracciones(true);
    setErrorInteracciones(null);
    try {
      const datos = await obtenerInteracciones(lead.id);
      setInteracciones(datos);
    } catch {
      setErrorInteracciones('No se pudo cargar el historial de interacciones.');
    } finally {
      setCargandoInteracciones(false);
    }
  };

  const manejarGuardarInteraccion = async (datosInteraccion) => {
    const nuevaInteraccion = await crearInteraccion(leadSeleccionado.id, datosInteraccion);
    setInteracciones((prev) => [nuevaInteraccion, ...prev]);
    mostrarToast('Interacción registrada ✓');
  };

  // --- Handlers de Tareas ---

  const manejarGuardarTarea = async (datosTarea) => {
    if (tareaEditar) {
      const tareaActualizada = await actualizarTarea(tareaEditar.id, datosTarea);
      setTareas((prev) =>
        prev.map((t) => (t.id === tareaActualizada.id ? tareaActualizada : t))
      );
      setTareaEditar(null);
      mostrarToast('Tarea actualizada con éxito ✓');
    } else {
      const tareaGuardada = await crearTarea(datosTarea);
      setTareas((prev) => [tareaGuardada, ...prev]);
      mostrarToast('Tarea creada con éxito ✓');
    }
  };

  const manejarEditarTarea = (tarea) => {
    setTareaEditar(tarea);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const manejarEliminarTarea = async (id) => {
    await eliminarTarea(id);
    setTareas((prev) => prev.filter((t) => t.id !== id));
    mostrarToast('Tarea eliminada ✓');
  };

  const manejarCancelarEdicionTarea = () => setTareaEditar(null);

  /**
   * Marca una tarea como Completada directamente desde la tabla,
   * sin necesidad de abrir el formulario de edición.
   */
  const manejarCompletarTarea = async (tarea) => {
    const tareaActualizada = await actualizarTarea(tarea.id, { estado: 'Completada' });
    setTareas((prev) =>
      prev.map((t) => (t.id === tareaActualizada.id ? tareaActualizada : t))
    );
    mostrarToast('Tarea marcada como completada ✓');
  };

  // Contador de tareas pendientes para mostrar en el tab
  const tareasPendientes = tareas.filter(
    (t) => t.estado === 'Pendiente' || t.estado === 'En Progreso'
  ).length;

  return (
    <>
      {toast && <div className="toast-notification">{toast}</div>}

      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo">CRM</div>
          <div>
            <h1 className="brand-title">Gestión Inmobiliaria</h1>
            <span className="header-subtitle">Proyecto Capstone</span>
          </div>
        </div>

        <div className="header-right">
          <div className="db-indicator">
            <span className="dot"></span>
            <span>Base de Datos: Supabase</span>
          </div>

          <nav className="nav-tabs">
            <button
              className={`tab-btn ${pestañaActiva === 'leads' ? 'active' : ''}`}
              onClick={() => setPestañaActiva('leads')}
            >
              Leads ({leads.length})
            </button>
            <button
              className={`tab-btn ${pestañaActiva === 'propiedades' ? 'active' : ''}`}
              onClick={() => setPestañaActiva('propiedades')}
            >
              Propiedades ({propiedades.length})
            </button>
            <button
              className={`tab-btn ${pestañaActiva === 'tareas' ? 'active' : ''}`}
              onClick={() => setPestañaActiva('tareas')}
            >
              Tareas
              {tareasPendientes > 0 && (
                <span className="tab-badge">{tareasPendientes}</span>
              )}
            </button>
          </nav>
        </div>
      </header>

      <main className="main-content">

        {/* ── Pestaña Leads ── */}
        {pestañaActiva === 'leads' && (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">
                  {leadEditar ? `Editando Lead #${leadEditar.id}` : 'Nuevo Lead'}
                </h2>
                <span className="badge">Gestión de Leads</span>
              </div>
              <FormularioLead
                alGuardar={manejarGuardarLead}
                leadEditar={leadEditar}
                alCancelar={manejarCancelarEdicionLead}
              />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Leads Registrados ({leads.length})</h2>
              </div>
              <TablaLeads
                leads={leads}
                cargando={cargandoLeads}
                error={errorLeads}
                alEditar={manejarEditarLead}
                alEliminar={manejarEliminarLead}
                alVerHistorial={manejarVerHistorial}
                leadSeleccionadoId={leadSeleccionado?.id}
              />
            </div>

            {leadSeleccionado && (
              <div className="dashboard-card panel-historial">
                <div className="card-header">
                  <div>
                    <h2 className="card-title">Historial — {leadSeleccionado.nombre}</h2>
                    <span className="historial-subtitulo">{leadSeleccionado.email}</span>
                  </div>
                  <button
                    className="btn-cerrar-panel"
                    onClick={() => { setLeadSeleccionado(null); setInteracciones([]); }}
                    title="Cerrar historial"
                  >
                    ✕
                  </button>
                </div>
                <FormularioInteraccion
                  leadNombre={leadSeleccionado.nombre}
                  alGuardar={manejarGuardarInteraccion}
                />
                <div className="historial-separador">
                  <span>Interacciones anteriores ({interacciones.length})</span>
                </div>
                <HistorialInteracciones
                  interacciones={interacciones}
                  cargando={cargandoInteracciones}
                  error={errorInteracciones}
                />
              </div>
            )}
          </>
        )}

        {/* ── Pestaña Propiedades ── */}
        {pestañaActiva === 'propiedades' && (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">
                  {propiedadEditar ? `Editando Propiedad #${propiedadEditar.id}` : 'Nueva Propiedad'}
                </h2>
                <span className="badge">Catálogo Inmobiliario</span>
              </div>
              <FormularioPropiedad
                alGuardar={manejarGuardarPropiedad}
                propiedadEditar={propiedadEditar}
                alCancelar={manejarCancelarEdicionPropiedad}
              />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">Propiedades Registradas ({propiedades.length})</h2>
              </div>
              <TablaPropiedades
                propiedades={propiedades}
                cargando={cargandoPropiedades}
                error={errorPropiedades}
                alEditar={manejarEditarPropiedad}
                alEliminar={manejarEliminarPropiedad}
              />
            </div>
          </>
        )}

        {/* ── Pestaña Tareas ── */}
        {pestañaActiva === 'tareas' && (
          <>
            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">
                  {tareaEditar ? `Editando Tarea #${tareaEditar.id}` : 'Nueva Tarea'}
                </h2>
                <span className="badge">Gestión de Tareas</span>
              </div>
              <FormularioTarea
                alGuardar={manejarGuardarTarea}
                tareaEditar={tareaEditar}
                alCancelar={manejarCancelarEdicionTarea}
                leads={leads}
              />
            </div>

            <div className="dashboard-card">
              <div className="card-header">
                <h2 className="card-title">
                  Tareas ({tareas.length})
                </h2>
                {tareasPendientes > 0 && (
                  <span className="badge badge-pendientes">
                    {tareasPendientes} pendiente{tareasPendientes !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
              <TablaTareas
                tareas={tareas}
                leads={leads}
                cargando={cargandoTareas}
                error={errorTareas}
                alEditar={manejarEditarTarea}
                alEliminar={manejarEliminarTarea}
                alCompletar={manejarCompletarTarea}
              />
            </div>
          </>
        )}

      </main>
    </>
  );
}

export default App;

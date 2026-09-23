import React from 'react';
import Icono from './Iconos';

/**
 * Navegación lateral principal de la aplicación.
 *
 * Reemplaza las pestañas del header. En un sistema de gestión la navegación
 * lateral permite crecer en secciones sin comprimir el encabezado.
 *
 * Props:
 * - vistaActiva: identificador de la vista actual
 * - alCambiarVista: función que recibe el identificador de la vista a mostrar
 * - contadores: { leads, propiedades, tareasPendientes }
 * - usuario: usuario con la sesión activa
 * - alCerrarSesion: cierra la sesión
 */

/** Toma las iniciales del nombre para el avatar del pie. */
function iniciales(nombre = '') {
  return nombre
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0] || '')
    .join('');
}

// soloAdmin marca las secciones que no se muestran a un ejecutivo. Ocultarlas es
// una comodidad, no la protección: quien realmente bloquea el acceso es el backend.
const SECCIONES = [
  {
    titulo: 'General',
    items: [{ id: 'inicio', etiqueta: 'Inicio', icono: 'panel' }],
  },
  {
    titulo: 'Gestión',
    items: [
      { id: 'leads', etiqueta: 'Leads', icono: 'usuarios', contador: 'leads' },
      { id: 'propiedades', etiqueta: 'Propiedades', icono: 'edificio', contador: 'propiedades' },
      { id: 'tareas', etiqueta: 'Tareas', icono: 'tareas', contador: 'tareasPendientes', destacar: true },
    ],
  },
  {
    titulo: 'Administración',
    soloAdmin: true,
    items: [{ id: 'consumo', etiqueta: 'Consumo de IA', icono: 'tendencia' }],
  },
];

function Sidebar({ vistaActiva, alCambiarVista, contadores, usuario, alCerrarSesion }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-marca">
        <div className="marca-logo">CRM</div>
        <div className="marca-texto">
          <span className="marca-nombre">Gestión Inmobiliaria</span>
          <span className="marca-sub">Grupo 5</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {SECCIONES.filter(
          (seccion) => !seccion.soloAdmin || usuario?.rol === 'admin'
        ).map((seccion) => (
          <div key={seccion.titulo} style={{ marginBottom: '1rem' }}>
            <p className="nav-grupo-titulo">{seccion.titulo}</p>

            {seccion.items.map((item) => {
              const valor = item.contador ? contadores[item.contador] : null;
              // Las tareas pendientes se destacan en rojo; el resto es un conteo neutro
              const destacado = item.destacar && valor > 0;

              return (
                <button
                  key={item.id}
                  className={`nav-item ${vistaActiva === item.id ? 'activo' : ''}`}
                  onClick={() => alCambiarVista(item.id)}
                >
                  <Icono nombre={item.icono} />
                  <span className="nav-item-etiqueta">{item.etiqueta}</span>
                  {valor > 0 && (
                    <span className={`nav-contador ${destacado ? 'destacado' : ''}`}>
                      {valor}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-pie">
        {usuario && (
          <div className="sidebar-usuario">
            <div className="usuario-inicial">{iniciales(usuario.nombre)}</div>
            <div className="usuario-datos">
              <span className="usuario-nombre">{usuario.nombre}</span>
              <span className="usuario-email">
                {usuario.rol === 'admin' ? 'Administrador' : 'Ejecutivo'}
              </span>
            </div>
            <button className="btn-icono" onClick={alCerrarSesion} title="Cerrar sesión">
              <Icono nombre="salir" />
            </button>
          </div>
        )}

        <div className="estado-conexion">
          <span className="punto-estado" />
          <Icono nombre="baseDatos" tamano={12} />
          <span>Supabase conectado</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

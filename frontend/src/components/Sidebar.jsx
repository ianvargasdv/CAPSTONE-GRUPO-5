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
 */

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
];

function Sidebar({ vistaActiva, alCambiarVista, contadores }) {
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
        {SECCIONES.map((seccion) => (
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

import React, { useId, useRef, useState } from 'react';

const SECCIONES = [
  ['resumen', 'Resumen'],
  ['asistente', 'Asistente'],
  ['seguimiento', 'Seguimiento'],
  ['propiedades', 'Propiedades'],
];

export default function SeccionesFichaLead(contenidos) {
  const [activa, setActiva] = useState('resumen');
  const prefijo = useId();
  const botones = useRef([]);

  const seleccionar = (id, boton) => {
    setActiva(id);
    boton.closest('.drawer-cuerpo')?.scrollTo({ top: 0 });
  };

  const navegar = (evento, indice) => {
    let siguiente;
    if (evento.key === 'ArrowRight') siguiente = (indice + 1) % SECCIONES.length;
    else if (evento.key === 'ArrowLeft') siguiente = (indice + SECCIONES.length - 1) % SECCIONES.length;
    else if (evento.key === 'Home') siguiente = 0;
    else if (evento.key === 'End') siguiente = SECCIONES.length - 1;
    else return;
    evento.preventDefault();
    seleccionar(SECCIONES[siguiente][0], evento.currentTarget);
    botones.current[siguiente]?.focus();
  };

  return (
    <div className="ficha-organizada">
      <nav className="ficha-navegacion" role="tablist" aria-label="Secciones del cliente">
        {SECCIONES.map(([id, titulo], indice) => (
          <button key={id} ref={(nodo) => { botones.current[indice] = nodo; }} type="button"
            role="tab" id={`${prefijo}-${id}-tab`} aria-controls={`${prefijo}-${id}-panel`}
            aria-selected={activa === id} tabIndex={activa === id ? 0 : -1}
            onClick={(e) => seleccionar(id, e.currentTarget)} onKeyDown={(e) => navegar(e, indice)}>
            {titulo}
          </button>
        ))}
      </nav>
      {/* Ocultar conserva los formularios y las propuestas al cambiar de vista. */}
      {SECCIONES.map(([id]) => (
        <section key={id} role="tabpanel" id={`${prefijo}-${id}-panel`}
          aria-labelledby={`${prefijo}-${id}-tab`} hidden={activa !== id}
          className="ficha-contenido">
          {contenidos[id]}
        </section>
      ))}
    </div>
  );
}

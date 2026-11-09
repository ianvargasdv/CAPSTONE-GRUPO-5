import React from 'react';

export default function EstadoCarga({ children = 'Cargando…' }) {
  return <div className="state-message estado-carga" role="status" aria-live="polite">
    <span className="estado-carga-indicador" aria-hidden="true" /><span>{children}</span>
  </div>;
}

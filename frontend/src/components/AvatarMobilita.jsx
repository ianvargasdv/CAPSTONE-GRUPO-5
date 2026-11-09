import React from 'react';
import imagenMobilita from '../assets/mobilita.svg';

export default function AvatarMobilita({ tamano = 'normal', pensando = false, saludando = false, className = '' }) {
  return <span className={`mobilita-mascota mobilita-mascota-${tamano}${pensando ? ' pensando' : ''}${saludando ? ' saludando' : ''} ${className}`} aria-hidden="true">
    <img src={imagenMobilita} alt="" width="64" height="64" draggable={false} />
  </span>;
}

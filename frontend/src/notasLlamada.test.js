import test from 'node:test';
import assert from 'node:assert/strict';
import { textoDeAnalisisLlamada, textoDePropuesta, validarRespuestaLlamada } from './notasLlamada.js';

const propuesta = { resumen: 'Se revisó la búsqueda.', requisitos: ['Dos estacionamientos'], proxima_accion: 'Confirmar disponibilidad.' };

test('texto revisable conserva resumen, requisitos y acción', () => {
  const texto = textoDePropuesta(propuesta);
  assert.match(texto, /Se revisó la búsqueda/);
  assert.match(texto, /- Dos estacionamientos/);
  assert.match(texto, /Próxima acción propuesta:\nConfirmar disponibilidad/);
});

test('sin requisitos ni próxima acción no inventa secciones', () => {
  assert.equal(textoDePropuesta({ resumen: 'Falta confirmar.', requisitos: [], proxima_accion: null }), 'Falta confirmar.');
});

test('rechaza salidas inválidas antes de ofrecer el guardado', () => {
  for (const p of [null, {}, { ...propuesta, resumen: '  ' }, { ...propuesta, requisitos: 'texto' },
    { ...propuesta, requisitos: [null] }, { ...propuesta, requisitos: ['x'.repeat(601)] },
    { ...propuesta, proxima_accion: 6 }, { ...propuesta, requisitos: Array(9).fill('x') }]) {
    assert.throws(() => textoDePropuesta(p));
  }
});

test('rechaza texto que supera el límite del registro de contacto', () => {
  assert.throws(() => textoDePropuesta({ resumen: 'a'.repeat(1600), requisitos: Array(8).fill('b'.repeat(600)), proxima_accion: null }));
});

test('una respuesta de otro cliente o tipo no puede usarse', () => {
  const respuesta = { analisis: { id: 1, lead_id: 7, tipo: 'registro_llamada' }, propuesta };
  assert.equal(validarRespuestaLlamada(respuesta, 7), textoDePropuesta(propuesta));
  assert.throws(() => validarRespuestaLlamada(respuesta, 8));
  assert.throws(() => validarRespuestaLlamada({ ...respuesta, analisis: { id: 1, lead_id: 7, tipo: 'resumen' } }, 7));
});

test('el historial presenta JSON válido como texto y trata una salida dañada sin romper la ficha', () => {
  assert.equal(textoDeAnalisisLlamada(JSON.stringify(propuesta)), textoDePropuesta(propuesta));
  assert.match(textoDeAnalisisLlamada('salida inválida'), /No se pudo interpretar/);
});

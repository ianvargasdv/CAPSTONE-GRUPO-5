import test from 'node:test';
import assert from 'node:assert/strict';
import { paginar } from './paginacion.js';

test('todas las filas son accesibles sin repetir ni modificar el orden', () => {
  const original = Array.from({ length: 23 }, (_, i) => i);
  assert.deepEqual([1, 2, 3].flatMap(p => paginar(original, p).items), original);
  assert.equal(original.length, 23);
  assert.equal(paginar(original, 3).desde, 21);
  assert.equal(paginar(original, 3).hasta, 23);
});
test('vacío y página fuera de rango tras eliminar o filtrar', () => {
  assert.deepEqual(paginar([], 5), { items: [], actual: 1, paginas: 1, desde: 0, hasta: 0 });
  assert.equal(paginar([1, 2], 5).actual, 1);
  assert.equal(paginar([1], 0).actual, 1);
});
test('el tamaño elegido limita la página', () => {
  assert.equal(paginar(Array.from({ length: 30 }), 1, 25).items.length, 25);
});

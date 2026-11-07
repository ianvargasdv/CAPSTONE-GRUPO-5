import test from 'node:test';
import assert from 'node:assert/strict';
import { fotoPrincipal, fotoReferencial } from './presentacion.js';
test('selecciona principal o primera fotografía válida sin mutar datos', () => {
  const propiedad = {foto_principal:'https://example.test/principal.jpg',fotografias:['https://example.test/otra.jpg']};
  assert.equal(fotoPrincipal(propiedad), propiedad.foto_principal);
  assert.equal(fotoPrincipal({...propiedad,foto_principal:null}), propiedad.fotografias[0]);
  assert.equal(propiedad.fotografias.length,1);
});
test('descarta protocolos peligrosos y tolera registros sin fotos', () => {
  assert.equal(fotoPrincipal({foto_principal:'javascript:alert(1)',fotografias:['texto','data:image/png,x','https://example.test/foto.jpg']}),'https://example.test/foto.jpg');
  assert.equal(fotoPrincipal({fotografias:null}),null);
});
test('sólo la marca explícita identifica imágenes referenciales', () => {
  assert.equal(fotoReferencial('https://example.test/foto.jpg#referencial'),true);
  assert.equal(fotoReferencial('https://example.test/foto.jpg'),false);
  assert.equal(fotoReferencial(null),false);
});

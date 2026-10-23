import test from 'node:test';
import assert from 'node:assert/strict';
import { textoBusqueda, coincideBusqueda, fechaLocalISO, tareaVencida, filtrarCatalogo, clienteDeTarea, fechaDeTarea } from './presentacion.js';

test('búsqueda independiente de mayúsculas, espacios y tildes', () => {
  assert.equal(textoBusqueda('  ÑUÑOA  '),'nunoa');
  assert.ok(coincideBusqueda('nicolas','Nicolás Araya'));
  assert.ok(coincideBusqueda('penalolen',null,'Peñalolén'));
  assert.equal(coincideBusqueda('Macul',undefined,'Ñuñoa'),false);
  assert.ok(coincideBusqueda('',null));
});

test('fecha local no cambia al día UTC de otro huso horario', () => {
  const fecha=new Date(2026,9,16,0,15);
  assert.equal(fechaLocalISO(fecha),'2026-10-16');
});

test('vencidas excluye hoy, completadas y ausencia de fecha', () => {
  assert.ok(tareaVencida({estado:'Pendiente',fecha_limite:'2026-10-15'},'2026-10-16'));
  assert.ok(tareaVencida({estado:'En Progreso',fecha_limite:'2026-10-15'},'2026-10-16'));
  for (const tarea of [{estado:'Completada',fecha_limite:'2026-10-15'},
    {estado:'Pendiente',fecha_limite:'2026-10-16'}, {estado:'Pendiente',fecha_limite:null}]) {
    assert.equal(tareaVencida(tarea,'2026-10-16'),false);
  }
});

const catalogo=[
  {id:1,titulo:'Casa con jardín',comuna:'Peñalolén',tipo:'Casa',estado:'Disponible',tipo_operacion:'Compra',codigo_interno:'CAS-001'},
  {id:2,titulo:'Departamento',comuna:'Ñuñoa',tipo:'Departamento',estado:'Reservada',tipo_operacion:'Arriendo',codigo_interno:'DEP-002'},
];
test('combina búsqueda, operación, tipo y estado sin modificar el catálogo', () => {
  assert.deepEqual(filtrarCatalogo(catalogo,{busqueda:'penalolen',tipo:'Casa',estado:'Disponible',operacion:'Compra'}).map(p=>p.id),[1]);
  assert.deepEqual(filtrarCatalogo(catalogo,{operacion:'Arriendo'}).map(p=>p.id),[2]);
  assert.deepEqual(filtrarCatalogo(catalogo,{busqueda:'dep-002'}).map(p=>p.id),[2]);
  assert.equal(filtrarCatalogo(catalogo,{operacion:'Arriendo',tipo:'Casa'}).length,0);
  assert.equal(filtrarCatalogo(catalogo).length,2);
  assert.equal(catalogo.length,2);
});

test('distingue clientes aunque sus tareas tengan el mismo título', () => {
  const leads = [{id:1, nombre:'Cliente ficticio A'}, {id:2, nombre:'Cliente ficticio B'}];
  assert.equal(clienteDeTarea(1, leads), 'Cliente ficticio A');
  assert.equal(clienteDeTarea('2', leads), 'Cliente ficticio B');
  assert.notEqual(clienteDeTarea(1, leads), clienteDeTarea(2, leads));
  assert.equal(leads[0].nombre, 'Cliente ficticio A');
});

test('no inventa el nombre de un cliente ausente o no asociado', () => {
  for (const id of [null, undefined, '', 0]) assert.equal(clienteDeTarea(id), 'Sin cliente asociado');
  assert.equal(clienteDeTarea(99, []), 'Cliente no disponible');
  assert.equal(clienteDeTarea(1, [{id:1,nombre:'  '}]), 'Cliente no disponible');
  assert.equal(clienteDeTarea(1, [{id:1,nombre:null}]), 'Cliente no disponible');
});

test('actualiza el nombre al cambiar el cliente seleccionado', () => {
  const leads = [{id:5,nombre:'Primera persona'}, {id:6,nombre:'Segunda persona'}];
  let seleccionado = '5';
  assert.equal(clienteDeTarea(seleccionado, leads), 'Primera persona');
  seleccionado = '6';
  assert.equal(clienteDeTarea(seleccionado, leads), 'Segunda persona');
});

test('presenta la misma fecha sin convertirla de zona horaria', () => {
  assert.equal(fechaDeTarea('2026-10-19'), '19-10-2026');
  assert.equal(fechaDeTarea('2026-01-01'), '01-01-2026');
  assert.equal(fechaDeTarea(null), 'Sin fecha límite');
  assert.equal(fechaDeTarea('ayer'), 'Fecha no disponible');
  assert.equal(fechaDeTarea(['2026-10-19']), 'Fecha no disponible');
});

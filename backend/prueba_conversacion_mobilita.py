"""Conversaciones de varios pasos con proveedor simulado y SQLite temporal."""
import json
import unittest
from datetime import datetime, timedelta, timezone

import prueba_chat_tareas as base_chat
import models
import seguridad


class ConversacionMobilitaTest(unittest.TestCase):
    setUp = base_chat.ChatTareasTest.setUp
    pedir = base_chat.ChatTareasTest.pedir

    def organizar(self, bloques, mensaje, anterior=None):
        self.resultado['texto'] = json.dumps({'accion': 'organizar', 'cliente': None, 'titulo': None,
            'descripcion': None, 'aclaracion': None, 'bloques': bloques})
        return self.pedir('preparar', {'mensaje': mensaje, 'anterior_id': anterior})

    def bloque(self, cliente='Martin Reyes', titulo='Llamar nuevamente'):
        return {'cliente': cliente, 'operaciones': [{'tipo': 'crear_tarea', 'datos': {'titulo': titulo}}]}

    def ruta(self, p, accion, datos, usuario=None):
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token((usuario or self.uno).id)).encode())]
        prefijo = 'acciones' if accion == 'confirmar' else 'conversacion'
        return self.client.solicitar('POST', f"/api/asistente/{prefijo}/{p['id']}/{accion}", datos, cabeceras)

    def confirmar(self, p, usuario=None):
        return self.ruta(p, 'confirmar', {'confirmar': True, 'paso': p['paso']}, usuario)

    def elegir(self, p, id, usuario=None):
        return self.ruta(p, 'elegir', {'lead_id': id, 'paso': p['paso']}, usuario)

    def test_homonimos_se_eligen_sin_otra_llamada_al_modelo(self):
        p = self.organizar([self.bloque('Martin')], 'Prepara para Martin una tarea de seguimiento.').json()
        self.assertEqual(p['estado'], 'pendiente')  # Sólo hay un Martin inicialmente.
        otro = models.Lead(nombre='Martín Salas', email='salas@example.test', ejecutivo_id=self.uno.id)
        self.db.add(otro); self.db.commit()
        p = self.organizar([self.bloque('Martin')], 'Prepara para Martin una tarea de seguimiento.').json()
        self.assertEqual(p['estado'], 'aclarar')
        self.assertEqual(len(p['opciones_cliente']), 2)
        llamadas = self.mock.call_count
        elegido = self.elegir(p, otro.id).json()
        self.assertEqual(self.mock.call_count, llamadas)
        self.assertEqual(elegido['cliente_acciones'], 'Martín Salas')
        self.assertEqual(self.confirmar(elegido).status_code, 200)
        self.assertEqual(self.db.query(models.Tarea).one().lead_id, otro.id)
        self.assertEqual(self.elegir(p, self.lead.id).status_code, 409)

    def test_seleccion_no_admite_ids_ajenos_ni_otra_conversacion(self):
        otro = models.Lead(nombre='Martín Salas', email='salas@example.test', ejecutivo_id=self.uno.id)
        ajeno = models.Lead(nombre='Martín Ajeno', email='ajeno@example.test', ejecutivo_id=self.dos.id)
        self.db.add_all([otro, ajeno]); self.db.commit()
        p = self.organizar([self.bloque('Martin')], 'Prepara una tarea para Martin.').json()
        self.assertNotIn(ajeno.id, [c['id'] for c in p['opciones_cliente']])
        self.assertEqual(self.elegir(p, ajeno.id).status_code, 404)
        self.assertEqual(self.elegir(p, otro.id, self.dos).status_code, 404)

    def test_seleccion_revalida_una_reasignacion(self):
        otro = models.Lead(nombre='Martín Salas', email='salas@example.test', ejecutivo_id=self.uno.id)
        self.db.add(otro); self.db.commit()
        p = self.organizar([self.bloque('Martin')], 'Prepara una tarea para Martin.').json()
        otro.ejecutivo_id = self.dos.id; self.db.commit()
        self.assertEqual(self.elegir(p, otro.id).status_code, 404)

    def dos_bloques(self):
        return self.organizar([self.bloque(), self.bloque('Otra persona', 'Confirmar requisitos')],
            'Prepara un seguimiento para Martin Reyes y confirma requisitos con Otra persona.').json()

    def test_dos_clientes_se_confirman_por_separado_sin_repetir(self):
        p = self.dos_bloques()
        self.assertEqual(self.db.query(models.Tarea).count(), 0)
        r = self.confirmar(p); self.assertEqual(r.status_code, 200, r.text)
        siguiente = r.json()['siguiente']
        self.assertEqual([b['estado'] for b in siguiente['agenda']], ['guardado', 'pendiente'])
        self.assertEqual(self.db.query(models.Tarea).count(), 1)
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.assertEqual(self.db.query(models.Tarea).count(), 1)
        self.assertEqual(self.confirmar(siguiente).status_code, 200)
        self.assertEqual(self.db.query(models.Tarea).count(), 2)
        self.assertEqual(self.mock.call_count, 1)

    def test_no_confirma_siguiente_paso_con_token_viejo_o_ausente(self):
        p = self.dos_bloques()
        self.assertEqual(self.ruta(p, 'confirmar', {'confirmar': True}).status_code, 409)
        siguiente = self.confirmar(p).json()['siguiente']
        self.assertNotEqual(p['paso'], siguiente['paso'])
        self.assertEqual(self.db.query(models.Tarea).count(), 1)
        self.assertEqual(self.ruta(siguiente, 'confirmar', {'confirmar': True, 'paso': 'inventado'}).status_code, 409)

    def test_descartar_no_deshace_lo_guardado(self):
        p = self.dos_bloques()
        siguiente = self.confirmar(p).json()['siguiente']
        r = self.ruta(siguiente, 'descartar', {'paso': siguiente['paso'], 'todos': True})
        self.assertEqual(r.status_code, 200)
        self.assertEqual([b['estado'] for b in r.json()['agenda']], ['guardado', 'descartado'])
        self.assertEqual(self.db.query(models.Tarea).count(), 1)
        self.assertEqual(self.confirmar(siguiente).status_code, 409)

    def test_omitir_un_bloque_incompleto_permite_continuar(self):
        p = self.organizar([{'cliente': None, 'pregunta': '¿A quién debo corregir el nombre?'}, self.bloque()],
            'Corrige el nombre de un lead y prepara una tarea para Martin Reyes.').json()
        self.assertEqual(p['estado'], 'aclarar')
        r = self.ruta(p, 'descartar', {'paso': p['paso']}).json()
        self.assertEqual(r['estado'], 'pendiente')
        self.assertEqual(r['agenda'][0]['estado'], 'descartado')

    def test_nuevo_lead_pide_correo_y_conserva_el_perfil(self):
        b = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {
            'nombre': 'José Hernández', 'tipo_propiedad_buscada': 'Casa'}}]}
        p = self.organizar([b], 'Agrega a José Hernández, interesado en una casa.').json()
        self.assertEqual(p['estado'], 'aclarar')
        self.assertIn('correo', p['mensaje'])
        self.assertEqual(self.db.query(models.Lead).count(), 2)
        completo = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {'email': 'jose@example.test'}}]}
        r = self.organizar([completo], 'Su correo es jose@example.test', p['id'])
        self.assertEqual(r.status_code, 201, r.text)
        nuevo = r.json(); self.assertEqual(nuevo['estado'], 'pendiente', nuevo)
        contexto = json.loads(self.mock.call_args.args[0])
        self.assertEqual(contexto['pendiente']['solicitud_actual']['cliente'], 'José Hernández')
        self.assertEqual(self.confirmar(nuevo).status_code, 200)
        lead = self.db.query(models.Lead).filter_by(email='jose@example.test').one()
        self.assertEqual(lead.nombre, 'José Hernández')
        self.assertEqual(lead.tipo_propiedad_buscada, 'Casa')
        self.assertEqual(lead.ejecutivo_id, self.uno.id)
        self.assertIsNone(lead.presupuesto_max)

    def test_creacion_duplicada_no_repite_ficha(self):
        b = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {'nombre': 'José Hernández', 'email': self.lead.email}}]}
        p = self.organizar([b], f'Agrega a José Hernández, correo {self.lead.email}').json()
        self.assertEqual(self.confirmar(p).status_code, 409)
        self.assertEqual(self.db.query(models.Lead).count(), 2)

    def test_creacion_no_acepta_roles_o_responsables(self):
        for campo in ['rol', 'ejecutivo_id', 'archivado']:
            b = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {
                'nombre': 'José Hernández', 'email': 'jose@example.test', campo: 'admin'}}]}
            p = self.organizar([b], 'Agrega a José Hernández, jose@example.test').json()
            self.assertEqual(p['estado'], 'aclarar')
            self.assertFalse(p['acciones'])

    def test_nombre_y_correo_inventados_no_se_ofrecen(self):
        b = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {'nombre': 'Nombre inventado', 'email': 'inventado@example.test'}}]}
        self.assertEqual(self.organizar([b], 'Agrega a José Hernández.').status_code, 502)

    def test_corregir_nombre_conserva_identidad_e_historial(self):
        self.db.add(models.Interaccion(lead_id=self.lead.id, tipo='Llamada', notas='Historial previo')); self.db.commit()
        b = {'cliente': 'Martin Reyes', 'operaciones': [{'tipo': 'corregir_nombre', 'datos': {'nombre': 'Martín Reyes Soto'}}]}
        p = self.organizar([b], 'Corrige el nombre de Martin Reyes a Martín Reyes Soto, es la misma persona.').json()
        self.assertEqual(p['acciones'][0]['antes']['nombre'], 'Martín Reyes')
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.db.refresh(self.lead)
        self.assertEqual(self.lead.nombre, 'Martín Reyes Soto')
        self.assertEqual(self.db.query(models.Interaccion).one().lead_id, self.lead.id)
        self.assertEqual(self.lead.email, 'martin@example.test')

    def test_aclarar_segundo_bloque_no_repite_primero(self):
        p = self.organizar([self.bloque(), {'cliente': 'Otra persona', 'pregunta': '¿Qué tarea necesitas?', 'operaciones': []}],
            'Prepara una tarea para Martin Reyes y otra para Otra persona, aún no sé cuál.').json()
        s = self.confirmar(p).json()['siguiente']
        self.assertEqual(s['estado'], 'aclarar')
        r = self.organizar([self.bloque('Otra persona', 'Llamar mañana')], 'Para Otra persona, llamar mañana.', s['id'])
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual([b['estado'] for b in r.json()['agenda']], ['guardado', 'pendiente'])
        self.assertEqual(self.confirmar(r.json()).status_code, 200)
        self.assertEqual(self.db.query(models.Tarea).count(), 2)
        self.assertEqual(self.ruta(s, 'descartar', {'paso': s['paso']}).status_code, 409)

    def test_una_pregunta_de_uso_no_pierde_la_solicitud(self):
        p = self.organizar([{'cliente': 'Martin Reyes', 'pregunta': '¿Para qué fecha?', 'operaciones': []}],
            'Quiero una tarea para Martin Reyes.').json()
        self.resultado['texto'] = json.dumps({'accion': 'responder', 'cliente': None, 'titulo': None, 'descripcion': None,
            'aclaracion': 'La fecha límite indica cuándo debes realizar el seguimiento.'})
        r = self.pedir('preparar', {'mensaje': '¿Qué significa fecha límite?', 'anterior_id': p['id']}).json()
        self.assertEqual(r['agenda'][0]['estado'], 'pendiente')
        self.assertIn('fecha límite', r['mensaje'])

    def test_otro_usuario_y_propuesta_vencida_no_eligen_ni_confirman(self):
        p = self.dos_bloques()
        self.assertEqual(self.confirmar(p, self.admin).status_code, 404)
        self.db.get(models.PropuestaTareaChat, p['id']).fecha_creacion = datetime.now(timezone.utc) - timedelta(minutes=31)
        self.db.commit()
        self.assertEqual(self.confirmar(p).status_code, 409)

    def test_una_propuesta_pendiente_no_se_rama_por_la_api(self):
        p = self.dos_bloques()
        llamadas = self.mock.call_count
        r = self.organizar([self.bloque()], 'Otra tarea para Martin Reyes', p['id'])
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.mock.call_count, llamadas)

    def test_corregir_un_paso_no_descarta_los_demas(self):
        p = self.dos_bloques()
        ajustado = self.ruta(p, 'ajustar', {'paso': p['paso']}).json()
        self.assertEqual(ajustado['estado'], 'aclarar')
        self.assertFalse(ajustado['acciones'])
        self.assertEqual(self.confirmar(p).status_code, 409)
        corregido = self.organizar([self.bloque('Martin Reyes', 'Confirmar horario de llamada')],
            'Cambia el título a Confirmar horario de llamada.', ajustado['id']).json()
        self.assertEqual(len(corregido['agenda']), 2)
        self.assertEqual(self.confirmar(corregido).status_code, 200)
        self.assertEqual(self.db.query(models.Tarea).one().titulo, 'Confirmar horario de llamada')

    def test_ajustar_plan_simple_conserva_datos_sin_escribir(self):
        self.resultado['texto'] = json.dumps({'accion': 'gestionar', 'cliente': 'Martin Reyes',
            'titulo': None, 'descripcion': None, 'aclaracion': None,
            'operaciones': [{'tipo': 'crear_tarea', 'datos': {'titulo': 'Volver a llamar'}}]})
        p = self.pedir('preparar', {'mensaje': 'Para Martin Reyes, crea Volver a llamar.'}).json()
        r = self.ruta(p, 'ajustar', {}).json()
        self.assertEqual(r['estado'], 'aclarar')
        self.assertEqual(r['agenda'][0]['acciones'], ['Crear tarea'])
        self.assertEqual(self.db.query(models.Tarea).count(), 0)

    def test_muchas_aclaraciones_conservan_la_ficha_original(self):
        b = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {
            'nombre': 'José Hernández', 'tipo_propiedad_buscada': 'Casa'}}]}
        p = self.organizar([b], 'Agrega a José Hernández, busca una casa.').json()
        for _ in range(7):
            self.resultado['texto'] = json.dumps({'accion': 'responder', 'cliente': None, 'titulo': None,
                'descripcion': None, 'aclaracion': 'Necesito un correo para identificar la ficha nueva.'})
            p = self.pedir('preparar', {'mensaje': 'Explícame ese dato, por favor.', 'anterior_id': p['id']}).json()
            self.assertEqual(p['agenda'][0]['cliente'], 'José Hernández')
        completo = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {'email': 'jose@example.test'}}]}
        r = self.organizar([completo], 'Usa jose@example.test', p['id']).json()
        self.assertEqual(r['estado'], 'pendiente')
        self.assertEqual(r['acciones'][0]['datos']['tipo_propiedad_buscada'], 'Casa')

    def test_limites_no_ejecutan_lotes_grandes(self):
        r = self.organizar([self.bloque()] * 6, 'Prepara tareas para Martin Reyes.')
        self.assertEqual(r.status_code, 502)
        self.assertEqual(self.db.query(models.Tarea).count(), 0)

    def test_pregunta_ajena_no_pierde_el_pendiente_ni_abre_permisos(self):
        p = self.organizar([{'cliente': 'Martin Reyes', 'pregunta': '¿Qué tarea necesitas?'}], 'Prepara una tarea para Martin Reyes.').json()
        self.resultado['texto'] = json.dumps({'accion': 'fuera_de_alcance', 'cliente': None,
            'titulo': None, 'descripcion': None, 'aclaracion': None})
        r = self.pedir('preparar', {'mensaje': '¿Cómo está el clima?', 'anterior_id': p['id']}).json()
        self.assertIn('Sólo puedo ayudarte con este CRM', r['mensaje'])
        self.assertEqual(r['agenda'][0]['estado'], 'pendiente')

    def test_opciones_dejan_de_exponer_cartera_reasignada(self):
        otro = models.Lead(nombre='Martín Salas', email='salas@example.test', ejecutivo_id=self.uno.id)
        self.db.add(otro); self.db.commit()
        p = self.organizar([self.bloque('Martin')], 'Tarea para Martin.').json()
        otro.ejecutivo_id = self.dos.id; self.db.commit()
        from tareas_chat import respuesta
        actual = respuesta(self.db.get(models.PropuestaTareaChat, p['id']), self.db, self.uno)
        self.assertNotIn(otro.id, [c['id'] for c in actual['opciones_cliente']])

    def test_referencias_de_tareas_iguales_son_distinguibles(self):
        self.db.add_all([models.Tarea(lead_id=self.lead.id, titulo='Llamar', estado='Pendiente'),
                         models.Tarea(lead_id=self.lead.id, titulo='Llamar', estado='Completada')])
        self.db.commit()
        b = {'cliente': 'Martin Reyes', 'operaciones': [{'tipo': 'actualizar_tarea', 'referencia': 'Llamar', 'datos': {'estado': 'Completada'}}]}
        p = self.organizar([b], 'Completa Llamar para Martin Reyes.').json()
        self.assertEqual(p['estado'], 'aclarar')
        self.assertIn('Pendiente', p['mensaje']); self.assertIn('Completada', p['mensaje'])

    def test_regresion_formato_de_perfil_no_solicita_campos_internos(self):
        b = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {
            'nombre': 'José Hernández', 'perfil_comercial': {'tipo_propiedad_buscada': 'Casa'}}}]}
        p = self.organizar([b], 'Agrega a José Hernández, busca una casa.').json()
        self.assertEqual(p['estado'], 'aclarar')
        self.assertIn('correo', p['mensaje'])
        self.assertNotIn('perfil_comercial', p['mensaje'])
        corregido = {'cliente': 'José Hernández', 'operaciones': [{'tipo': 'crear_lead', 'datos': {
            'email': 'jose@example.test', 'tipo_propiedad_buscada': 'Casa'}}]}
        r = self.organizar([corregido], 'El correo es jose@example.test.', p['id']).json()
        self.assertEqual(r['estado'], 'pendiente')
        self.assertNotIn('perfil_comercial', r['acciones'][0]['datos'])
        self.assertEqual(self.confirmar(r).status_code, 200)
        self.assertEqual(self.db.query(models.Lead).filter_by(email='jose@example.test').one().tipo_propiedad_buscada, 'Casa')


if __name__ == '__main__':
    unittest.main()

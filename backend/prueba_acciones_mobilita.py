"""Acciones confirmadas y buzón con SQLite temporal, sin llamadas al proveedor."""
import json
import unittest
from datetime import datetime, timedelta, timezone

import prueba_chat_tareas as base_chat
import models
import seguridad


class AccionesMobilitaTest(unittest.TestCase):
    setUp = base_chat.ChatTareasTest.setUp
    pedir = base_chat.ChatTareasTest.pedir

    def preparar(self, ops, cliente='Martin Reyes', usuario=None):
        self.resultado['texto'] = json.dumps({'accion': 'gestionar', 'cliente': cliente,
            'titulo': None, 'descripcion': None, 'aclaracion': None, 'operaciones': ops})
        return self.pedir('preparar', {'mensaje': f'Para {cliente}: registra lo conversado y el seguimiento.'}, usuario)

    def confirmar(self, p, usuario=None):
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token((usuario or self.uno).id)).encode())]
        return self.client.solicitar('POST', f"/api/asistente/acciones/{p['id']}/confirmar", {'confirmar': True}, cabeceras)

    def buzon(self, usuario=None, id=None, datos=None):
        ruta = '/api/asistente/solicitudes' + (f'/{id}/resolver' if id else '')
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token((usuario or self.uno).id)).encode())]
        return self.client.solicitar('POST' if id else 'GET', ruta, datos, cabeceras)

    def contacto(self):
        return {'tipo': 'registrar_contacto', 'datos': {'tipo': 'Llamada', 'notas': 'Confirmé sus requisitos.'}}

    def solicitud(self):
        return {'tipo': 'solicitar_archivo', 'datos': {'motivo': 'El cliente pidió no continuar.'}}

    def test_preparar_y_cancelar_no_modifica_contactos_ni_lead(self):
        p = self.preparar([self.contacto()]).json()
        self.assertEqual(p['estado'], 'pendiente', p)
        self.assertEqual(self.db.query(models.Interaccion).count(), 0)
        self.assertEqual(self.pedir(f"{p['id']}/cancelar").status_code, 200)
        self.assertEqual(self.confirmar(p).status_code, 409)
        self.assertEqual(self.db.query(models.Interaccion).count(), 0)

    def test_contacto_estado_y_tarea_son_una_confirmacion_idempotente(self):
        p = self.preparar([self.contacto(), {'tipo': 'actualizar_lead', 'datos': {'estado': 'Contactado'}},
            {'tipo': 'crear_tarea', 'datos': {'titulo': 'Volver a llamar', 'fecha_limite': '2026-11-10'}}]).json()
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.assertEqual(self.db.query(models.Interaccion).count(), 1)
        self.assertEqual(self.db.query(models.Tarea).count(), 1)
        self.db.refresh(self.lead)
        self.assertEqual(self.lead.estado, 'Contactado')
        self.assertGreaterEqual(self.db.query(models.Auditoria).count(), 4)

    def test_no_puede_usar_confirmacion_de_otro_usuario(self):
        p = self.preparar([self.contacto()]).json()
        self.assertEqual(self.confirmar(p, self.admin).status_code, 404)
        self.assertEqual(self.confirmar(p, self.dos).status_code, 404)

    def test_reasignacion_invalida_propuesta_y_no_filtra_cartera_ajena(self):
        p = self.preparar([self.contacto()]).json()
        self.lead.ejecutivo_id = self.dos.id; self.db.commit()
        self.assertEqual(self.confirmar(p).status_code, 404)
        r = self.preparar([self.contacto()]).json()
        self.assertEqual(r['estado'], 'aclarar')
        self.assertFalse(r['clientes'])
        self.assertEqual(self.db.query(models.Interaccion).count(), 0)

    def test_error_en_segunda_accion_revierte_primera_y_auditoria(self):
        self.db.add(models.Tarea(lead_id=self.lead.id, titulo='Volver a llamar', estado='Pendiente')); self.db.commit()
        p = self.preparar([self.contacto(), {'tipo': 'crear_tarea', 'datos': {'titulo': 'Volver a llamar'}}]).json()
        self.assertEqual(self.confirmar(p).status_code, 409)
        self.assertEqual(self.db.query(models.Interaccion).count(), 0)
        self.assertEqual(self.db.query(models.Auditoria).filter_by(entidad='interaccion').count(), 0)
        self.assertEqual(self.db.get(models.PropuestaTareaChat, p['id']).estado, 'pendiente')

    def test_cliente_ambiguo_exige_aclaracion(self):
        self.db.add(models.Lead(nombre='Martín Reyes Segundo', email='segundo@example.test', ejecutivo_id=self.uno.id)); self.db.commit()
        r = self.preparar([self.contacto()]).json()
        self.assertEqual(r['estado'], 'aclarar')
        self.assertIsNone(r['acciones'])

    def test_no_hay_herramienta_de_borrado_roles_ni_cambios_masivos(self):
        for op in [{'tipo': 'borrar_lead', 'datos': {}},
                   {'tipo': 'actualizar_lead', 'datos': {'ejecutivo_id': self.dos.id}},
                   {'tipo': 'actualizar_lead', 'datos': {'rol': 'admin'}},
                   {'tipo': 'actualizar_lead', 'datos': {'nombre': 'Otro nombre'}}]:
            self.assertEqual(self.preparar([op]).status_code, 502)
        self.assertEqual(self.preparar([self.contacto()] * 6).status_code, 502)

    def test_datos_invalidos_no_preparan_cambios(self):
        for op in [{'tipo': 'crear_tarea', 'datos': {'titulo': '', 'fecha_limite': 'ayer'}},
                   {'tipo': 'actualizar_lead', 'datos': {'estado': 'Urgente'}},
                   {'tipo': 'solicitar_archivo', 'datos': {'motivo': ' '}},
                   {'tipo': 'actualizar_lead', 'datos': {}}]:
            self.assertEqual(self.preparar([op]).status_code, 502)

    def test_presupuesto_invalido_no_se_guarda(self):
        self.lead.presupuesto_min = 100; self.db.commit()
        p = self.preparar([{'tipo': 'actualizar_lead', 'datos': {'presupuesto_max': 50}}]).json()
        self.assertEqual(self.confirmar(p).status_code, 422)
        self.db.refresh(self.lead); self.assertIsNone(self.lead.presupuesto_max)

    def test_completar_y_reprogramar_tarea(self):
        t = models.Tarea(lead_id=self.lead.id, titulo='Confirmar requisitos', estado='Pendiente')
        self.db.add(t); self.db.commit()
        p = self.preparar([{'tipo': 'actualizar_tarea', 'referencia': t.titulo,
                            'datos': {'estado': 'Completada', 'fecha_limite': '2026-11-11'}}]).json()
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.db.refresh(t); self.assertEqual(t.estado, 'Completada')
        self.assertEqual(str(t.fecha_limite), '2026-11-11')

    def test_edicion_intermedia_no_sobrescribe_tarea(self):
        t = models.Tarea(lead_id=self.lead.id, titulo='Confirmar requisitos', estado='Pendiente')
        self.db.add(t); self.db.commit()
        p = self.preparar([{'tipo': 'actualizar_tarea', 'referencia': t.titulo, 'datos': {'estado': 'Completada'}}]).json()
        t.estado = 'En Progreso'; self.db.commit()
        self.assertEqual(self.confirmar(p).status_code, 409)
        self.db.refresh(t); self.assertEqual(t.estado, 'En Progreso')

    def propiedad(self, titulo='Casa de prueba'):
        p = models.Propiedad(titulo=titulo, precio=100, direccion='Dirección ficticia', estado='Disponible')
        self.db.add(p); self.db.commit(); return p

    def test_propiedad_ambigua_no_se_elige_automaticamente(self):
        self.propiedad('Departamento Ñuñoa uno'); self.propiedad('Departamento Ñuñoa dos')
        r = self.preparar([{'tipo': 'asociar_propiedad', 'referencia': 'Ñuñoa', 'datos': {}}]).json()
        self.assertEqual(r['estado'], 'aclarar')
        self.assertEqual(self.db.query(models.Interes).count(), 0)

    def test_asociar_propiedad_y_duplicado(self):
        prop = self.propiedad()
        op = {'tipo': 'asociar_propiedad', 'referencia': prop.titulo, 'datos': {'nivel_interes': 'Alto'}}
        self.assertEqual(self.confirmar(self.preparar([op]).json()).status_code, 200)
        self.assertEqual(self.confirmar(self.preparar([op]).json()).status_code, 409)
        self.assertEqual(self.db.query(models.Interes).count(), 1)

    def test_agendar_reprogramar_y_comprobar_cruce(self):
        prop = self.propiedad()
        op = {'tipo': 'agendar_visita', 'referencia': prop.titulo, 'datos': {'fecha_hora': '2026-11-12T10:00:00-03:00'}}
        p = self.preparar([op]).json()
        r = self.confirmar(p); self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(self.confirmar(self.preparar([op]).json()).status_code, 409)
        op['tipo'] = 'reprogramar_visita'; op['datos']['fecha_hora'] = '2026-11-12T12:00:00-03:00'
        r = self.confirmar(self.preparar([op]).json()); self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(self.db.query(models.Visita).count(), 1)

    def test_visita_sin_zona_horaria_y_propiedad_retirada(self):
        prop = self.propiedad()
        op = {'tipo': 'agendar_visita', 'referencia': prop.titulo, 'datos': {'fecha_hora': '2026-11-12T10:00:00'}}
        self.assertEqual(self.preparar([op]).status_code, 502)
        op['datos']['fecha_hora'] += '-03:00'
        p = self.preparar([op]).json(); prop.estado = 'Retirada'; self.db.commit()
        self.assertEqual(self.confirmar(p).status_code, 409)

    def test_solicitud_no_archiva_hasta_aprobacion_y_no_se_duplica(self):
        p = self.preparar([self.solicitud()]).json()
        self.assertEqual(self.db.query(models.SolicitudArchivo).count(), 0)
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.db.refresh(self.lead); self.assertFalse(self.lead.archivado)
        self.assertEqual(self.confirmar(self.preparar([self.solicitud()]).json()).status_code, 409)
        solicitud = self.buzon().json()[0]
        self.assertEqual(self.buzon(self.dos).json(), [])
        datos = {'decision': 'Aprobada', 'motivo': 'Solicitud revisada.'}
        self.assertEqual(self.buzon(id=solicitud['id'], datos=datos).status_code, 403)
        self.assertEqual(self.buzon(self.admin, solicitud['id'], datos).status_code, 200)
        self.db.refresh(self.lead); self.assertTrue(self.lead.archivado)
        self.assertEqual(self.lead.estado, 'Cerrado')
        self.assertEqual(self.buzon(self.admin, solicitud['id'], datos).status_code, 409)

    def test_rechazar_conserva_lead_y_contactos(self):
        self.db.add(models.Interaccion(lead_id=self.lead.id, tipo='Llamada', notas='Historial previo')); self.db.commit()
        self.confirmar(self.preparar([self.solicitud()]).json())
        s = self.buzon().json()[0]
        self.assertEqual(self.buzon(self.admin, s['id'], {'decision': 'Rechazada', 'motivo': 'Continuar seguimiento.'}).status_code, 200)
        self.db.refresh(self.lead); self.assertFalse(self.lead.archivado)
        self.assertEqual(self.db.query(models.Interaccion).count(), 1)

    def test_propuesta_vencida_no_guarda(self):
        p = self.preparar([self.contacto()]).json()
        self.db.get(models.PropuestaTareaChat, p['id']).fecha_creacion = datetime.now(timezone.utc) - timedelta(minutes=31)
        self.db.commit(); self.assertEqual(self.confirmar(p).status_code, 409)

    def test_delete_directo_tambien_requiere_admin(self):
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token(self.uno.id)).encode())]
        r = self.client.solicitar('DELETE', f'/api/leads/{self.lead.id}', cabeceras=cabeceras)
        self.assertEqual(r.status_code, 403)

    def test_formularios_no_permiten_escribir_en_cartera_ajena(self):
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token(self.dos.id)).encode())]
        for metodo, ruta, datos in [
            ('PUT', f'/api/leads/{self.lead.id}', {'estado': 'Contactado'}),
            ('POST', f'/api/leads/{self.lead.id}/interacciones', {'tipo': 'Llamada', 'notas': 'No autorizado'}),
        ]:
            r = self.client.solicitar(metodo, ruta, datos, cabeceras)
            self.assertEqual(r.status_code, 404, r.text)
        self.assertEqual(self.db.query(models.Interaccion).count(), 0)

    def test_archivo_conserva_historial_y_retira_lead_activo(self):
        self.db.add(models.Interaccion(lead_id=self.lead.id, tipo='Llamada', notas='Contacto previo'))
        self.db.commit()
        self.confirmar(self.preparar([self.solicitud()]).json())
        s = self.buzon().json()[0]
        self.buzon(self.admin, s['id'], {'decision': 'Aprobada', 'motivo': 'Cliente no desea continuar.'})
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token(self.uno.id)).encode())]
        r = self.client.solicitar('GET', '/api/leads?cartera=mia', cabeceras=cabeceras)
        self.assertNotIn(self.lead.id, [l['id'] for l in r.json()])
        self.assertEqual(self.db.query(models.Interaccion).count(), 1)
        self.assertIsNotNone(self.db.get(models.Lead, self.lead.id))

    def test_confirmacion_no_acepta_operaciones_desde_el_navegador(self):
        p = self.preparar([self.contacto()]).json()
        cabeceras = [(b'authorization', ('Bearer '+seguridad.crear_token(self.uno.id)).encode())]
        r = self.client.solicitar('POST', f"/api/asistente/acciones/{p['id']}/confirmar",
            {'confirmar': True, 'operaciones': [{'tipo': 'borrar_lead'}]}, cabeceras)
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self.db.query(models.Interaccion).count(), 0)

    def test_un_lead_cerrado_puede_solicitar_archivo_sin_reabrirse(self):
        self.lead.estado = 'Cerrado'; self.db.commit()
        p = self.preparar([self.solicitud()]).json()
        self.assertEqual(p['estado'], 'pendiente')
        self.assertEqual(self.confirmar(p).status_code, 200)
        self.db.refresh(self.lead)
        self.assertEqual(self.lead.estado, 'Cerrado')
        self.assertFalse(self.lead.archivado)


if __name__ == '__main__':
    unittest.main()

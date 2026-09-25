"""Carga un escenario ficticio y coherente para demostrar el CRM.

Los nombres, correos, teléfonos y direcciones son inventados. Los correos usan el
dominio reservado ``example.test`` y los teléfonos una numeración imposible, para
evitar confundirlos con personas reales. El proceso es idempotente: puede ejecutarse
varias veces sin duplicar el escenario.

Uso, después de ejecutar ``python migrar.py``::

    python cargar_datos_demo.py
"""

from datetime import date, datetime, timedelta, timezone

import database
import models


LEADS = [
    {
        "nombre": "Camila Rojas (Demo)", "email": "camila.rojas@example.test",
        "telefono": "+56 9 0000 0001", "estado": "Calificado", "prioridad": "Alta",
        "tipo_operacion": "Compra", "presupuesto_min": 145_000_000,
        "presupuesto_max": 185_000_000, "moneda": "CLP",
        "comunas_interes": "Ñuñoa, Macul", "tipo_propiedad_buscada": "Departamento",
        "dormitorios_min": 2, "banos_min": 2, "plazo_decision": "0-3 meses",
        "financiamiento": "Crédito preaprobado", "origen": "Portal inmobiliario",
        "proxima_accion": "Enviar comparativo de tres departamentos y confirmar visita",
    },
    {
        "nombre": "Matías Fuentes (Demo)", "email": "matias.fuentes@example.test",
        "telefono": "+56 9 0000 0002", "estado": "Contactado", "prioridad": "Media",
        "tipo_operacion": "Arriendo", "presupuesto_min": 650_000,
        "presupuesto_max": 850_000, "moneda": "CLP",
        "comunas_interes": "Providencia, Santiago", "tipo_propiedad_buscada": "Departamento",
        "dormitorios_min": 1, "banos_min": 1, "plazo_decision": "Inmediato",
        "financiamiento": "Recursos propios", "origen": "Redes sociales",
        "proxima_accion": "Confirmar disponibilidad para visita después de las 18:00",
    },
    {
        "nombre": "Valentina Pérez (Demo)", "email": "valentina.perez@example.test",
        "telefono": "+56 9 0000 0003", "estado": "Nuevo", "prioridad": "Alta",
        "tipo_operacion": "Compra", "presupuesto_min": 210_000_000,
        "presupuesto_max": 280_000_000, "moneda": "CLP",
        "comunas_interes": "La Reina, Peñalolén", "tipo_propiedad_buscada": "Casa",
        "dormitorios_min": 3, "banos_min": 2, "plazo_decision": "3-6 meses",
        "financiamiento": "En evaluación", "origen": "Referido",
        "proxima_accion": "Llamar para completar requisitos de terreno y estacionamientos",
    },
    {
        "nombre": "Diego Morales (Demo)", "email": "diego.morales@example.test",
        "telefono": "+56 9 0000 0004", "estado": "Calificado", "prioridad": "Media",
        "tipo_operacion": "Compra", "presupuesto_min": 95_000_000,
        "presupuesto_max": 125_000_000, "moneda": "CLP",
        "comunas_interes": "San Miguel, La Cisterna", "tipo_propiedad_buscada": "Departamento",
        "dormitorios_min": 2, "banos_min": 1, "plazo_decision": "0-3 meses",
        "financiamiento": "Crédito preaprobado", "origen": "Sitio web",
        "proxima_accion": "Solicitar confirmación de renta antes de reservar visita",
    },
    {
        "nombre": "Fernanda Silva (Demo)", "email": "fernanda.silva@example.test",
        "telefono": "+56 9 0000 0005", "estado": "Contactado", "prioridad": "Baja",
        "tipo_operacion": "Compra", "presupuesto_min": 160_000_000,
        "presupuesto_max": 200_000_000, "moneda": "CLP",
        "comunas_interes": "Quilicura, Lampa", "tipo_propiedad_buscada": "Casa",
        "dormitorios_min": 3, "banos_min": 2, "plazo_decision": "6-12 meses",
        "financiamiento": "En evaluación", "origen": "Llamada",
        "proxima_accion": "Retomar contacto cuando finalice evaluación bancaria",
    },
]

PROPIEDADES = [
    {"titulo": "[DEMO] Departamento Plaza Ñuñoa", "tipo": "Departamento", "precio": 169_000_000, "direccion": "Sector Plaza Ñuñoa, Ñuñoa", "estado": "Disponible"},
    {"titulo": "[DEMO] Departamento Parque Macul", "tipo": "Departamento", "precio": 154_000_000, "direccion": "Sector Parque Macul, Macul", "estado": "Disponible"},
    {"titulo": "[DEMO] Casa Familiar La Reina", "tipo": "Casa", "precio": 259_000_000, "direccion": "Sector Príncipe de Gales, La Reina", "estado": "Disponible"},
    {"titulo": "[DEMO] Departamento Metro San Miguel", "tipo": "Departamento", "precio": 112_000_000, "direccion": "Sector Metro San Miguel, San Miguel", "estado": "Reservada"},
    {"titulo": "[DEMO] Departamento Barrio Italia", "tipo": "Departamento", "precio": 790_000, "direccion": "Sector Barrio Italia, Providencia", "estado": "Disponible"},
]


def cargar() -> tuple[int, int, int, int]:
    db = database.SessionLocal()
    nuevos_leads = 0
    nuevas_propiedades = 0
    nuevas_oportunidades = 0
    nuevas_visitas = 0
    hoy = date.today()
    ahora = datetime.now(timezone.utc)
    try:
        responsable = db.query(models.Usuario).filter(models.Usuario.activo.is_(True)).order_by(models.Usuario.id).first()
        leads = {}
        for indice, datos in enumerate(LEADS):
            lead = db.query(models.Lead).filter(models.Lead.email == datos["email"]).first()
            if not lead:
                lead = models.Lead(
                    **datos, es_demo=True, ejecutivo_id=responsable.id if responsable else None,
                    fecha_proxima_accion=hoy + timedelta(days=indice + 1),
                    fecha_creacion=ahora - timedelta(days=(indice + 1) * 4),
                )
                db.add(lead)
                db.flush()
                nuevos_leads += 1
            leads[datos["email"]] = lead

        propiedades = {}
        for datos in PROPIEDADES:
            propiedad = db.query(models.Propiedad).filter(models.Propiedad.titulo == datos["titulo"]).first()
            if not propiedad:
                propiedad = models.Propiedad(**datos)
                db.add(propiedad)
                db.flush()
                nuevas_propiedades += 1
            propiedades[datos["titulo"]] = propiedad

        relaciones = [
            ("camila.rojas@example.test", "[DEMO] Departamento Plaza Ñuñoa", "Alto", "Le gustó la conectividad y pidió revisar gastos comunes."),
            ("camila.rojas@example.test", "[DEMO] Departamento Parque Macul", "Medio", "Alternativa dentro del presupuesto."),
            ("matias.fuentes@example.test", "[DEMO] Departamento Barrio Italia", "Alto", "Necesita mudarse durante el mes."),
            ("valentina.perez@example.test", "[DEMO] Casa Familiar La Reina", "Alto", "Busca patio y cercanía a colegio."),
            ("diego.morales@example.test", "[DEMO] Departamento Metro San Miguel", "Medio", "Revisar si la reserva sigue vigente."),
        ]
        for correo, titulo, nivel, notas in relaciones:
            lead, propiedad = leads[correo], propiedades[titulo]
            existe = db.query(models.Interes).filter_by(lead_id=lead.id, propiedad_id=propiedad.id).first()
            if not existe:
                db.add(models.Interes(lead_id=lead.id, propiedad_id=propiedad.id, nivel_interes=nivel, notas=notas))

        contactos = [
            ("camila.rojas@example.test", "Llamada", "Confirmó crédito preaprobado y disponibilidad para visitar el sábado.", 1),
            ("camila.rojas@example.test", "WhatsApp", "Se enviaron fichas de Ñuñoa y Macul. Prefiere orientación norte.", 3),
            ("matias.fuentes@example.test", "WhatsApp", "Busca arriendo inmediato y acepta coordinar en horario vespertino.", 1),
            ("diego.morales@example.test", "Email", "Envió antecedentes iniciales para evaluación.", 5),
            ("fernanda.silva@example.test", "Llamada", "Pausó la búsqueda hasta terminar su evaluación bancaria.", 12),
        ]
        for correo, tipo, notas, dias in contactos:
            lead = leads[correo]
            existe = db.query(models.Interaccion).filter_by(lead_id=lead.id, tipo=tipo, notas=notas).first()
            if not existe:
                db.add(models.Interaccion(lead_id=lead.id, tipo=tipo, notas=notas, fecha_creacion=ahora - timedelta(days=dias)))

        tareas = [
            ("camila.rojas@example.test", "Confirmar visita del sábado", "Alta", 2),
            ("matias.fuentes@example.test", "Validar disponibilidad del arriendo", "Alta", 1),
            ("valentina.perez@example.test", "Completar calificación de vivienda", "Media", 3),
            ("diego.morales@example.test", "Revisar antecedentes de renta", "Media", 2),
        ]
        for correo, titulo, prioridad, dias in tareas:
            lead = leads[correo]
            existe = db.query(models.Tarea).filter_by(lead_id=lead.id, titulo=titulo).first()
            if not existe:
                db.add(models.Tarea(titulo=titulo, estado="Pendiente", prioridad=prioridad, fecha_limite=hoy + timedelta(days=dias), lead_id=lead.id))

        oportunidades = [
            ("camila.rojas@example.test", "[DEMO] Departamento Plaza Ñuñoa", "Compra", "Negociación", 169_000_000, 80, 14, None),
            ("matias.fuentes@example.test", "[DEMO] Departamento Barrio Italia", "Arriendo", "Visita", 790_000, 30, 5, None),
            ("valentina.perez@example.test", "[DEMO] Casa Familiar La Reina", "Compra", "Contacto", 259_000_000, 10, 45, None),
            ("diego.morales@example.test", "[DEMO] Departamento Metro San Miguel", "Compra", "Ganada", 112_000_000, 100, -2, "Oferta aceptada"),
            ("fernanda.silva@example.test", None, "Compra", "Perdida", 180_000_000, 0, -5, "Financiamiento no aprobado"),
        ]
        for correo, titulo, tipo, etapa, valor, probabilidad, dias, motivo in oportunidades:
            lead = leads[correo]
            propiedad = propiedades.get(titulo) if titulo else None
            consulta = db.query(models.Oportunidad).filter(models.Oportunidad.lead_id == lead.id)
            consulta = consulta.filter(
                models.Oportunidad.propiedad_id == propiedad.id
                if propiedad else models.Oportunidad.propiedad_id.is_(None)
            )
            if not consulta.first():
                db.add(models.Oportunidad(
                    lead_id=lead.id,
                    propiedad_id=propiedad.id if propiedad else None,
                    ejecutivo_id=responsable.id if responsable else None,
                    tipo_operacion=tipo,
                    etapa=etapa,
                    valor_estimado=valor,
                    moneda="CLP",
                    probabilidad=probabilidad,
                    fecha_cierre_estimada=hoy + timedelta(days=dias),
                    fecha_cierre=hoy + timedelta(days=dias) if etapa in {"Ganada", "Perdida"} else None,
                    motivo_cierre=motivo,
                    notas="Escenario ficticio para demostrar el pipeline del capstone.",
                ))
                nuevas_oportunidades += 1

        db.flush()
        visitas = [
            (
                "camila.rojas@example.test", "[DEMO] Departamento Plaza Ñuñoa",
                "Confirmada", 2, 60, "Presencial", None, None,
                "Preparar comparativo de gastos comunes",
            ),
            (
                "matias.fuentes@example.test", "[DEMO] Departamento Barrio Italia",
                "Programada", 4, 45, "Presencial", None, None,
                "Confirmar asistencia durante la mañana",
            ),
            (
                "valentina.perez@example.test", "[DEMO] Casa Familiar La Reina",
                "Programada", 7, 90, "Presencial", None, None,
                "Enviar ubicación y condiciones de visita",
            ),
            (
                "diego.morales@example.test", "[DEMO] Departamento Metro San Miguel",
                "Realizada", -3, 60, "Presencial",
                "Visitó la propiedad, valoró la cercanía al metro y solicitó antecedentes de la reserva.",
                None, "Verificar estado de la reserva con el propietario",
            ),
            (
                "fernanda.silva@example.test", "[DEMO] Casa Familiar La Reina",
                "Cancelada", -6, 60, "Virtual", None,
                "La clienta pausó la búsqueda mientras termina su evaluación bancaria.",
                "Retomar contacto al finalizar la evaluación bancaria",
            ),
        ]
        for indice, (correo, titulo, estado, dias, duracion, modalidad, resultado, motivo, proxima) in enumerate(visitas):
            lead, propiedad = leads[correo], propiedades[titulo]
            oportunidad = db.query(models.Oportunidad).filter_by(
                lead_id=lead.id, propiedad_id=propiedad.id
            ).first()
            existe = db.query(models.Visita).filter_by(
                lead_id=lead.id, proxima_accion=proxima
            ).first()
            if not existe:
                db.add(models.Visita(
                    lead_id=lead.id,
                    propiedad_id=propiedad.id,
                    oportunidad_id=oportunidad.id if oportunidad else None,
                    ejecutivo_id=responsable.id if responsable else None,
                    fecha_hora=ahora + timedelta(days=dias, hours=10 + indice),
                    duracion_minutos=duracion,
                    estado=estado,
                    modalidad=modalidad,
                    punto_encuentro=propiedad.direccion,
                    resultado=resultado,
                    motivo_cancelacion=motivo,
                    proxima_accion=proxima,
                ))
                nuevas_visitas += 1

        db.commit()
        return nuevos_leads, nuevas_propiedades, nuevas_oportunidades, nuevas_visitas
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cantidad_leads, cantidad_propiedades, cantidad_oportunidades, cantidad_visitas = cargar()
    print(
        f"Datos demo listos: {cantidad_leads} leads, {cantidad_propiedades} propiedades "
        f"{cantidad_oportunidades} oportunidades y {cantidad_visitas} visitas nuevas."
    )
    print("Los registros se distinguen por '(Demo)', '[DEMO]' y es_demo=true.")

"""
Reglas de negocio para priorizar leads.

El puntaje responde a una pregunta concreta del ejecutivo: de todos mis prospectos,
a quién tengo que atender primero. No es una predicción ni un modelo estadístico,
son reglas explícitas sobre hechos observables del CRM.

Cada puntaje viene acompañado de los motivos que lo produjeron. Eso cumple dos
propósitos: que la priorización se pueda explicar y auditar, y que más adelante el
agente de IA tenga de dónde partir para redactar una recomendación en lenguaje
natural en lugar de inventarla.

Los umbrales y los puntos están como constantes con nombre para que ajustar el
criterio no implique buscar números sueltos en medio del código.
"""

from datetime import datetime, timezone

# ── Lead que nunca fue contactado ──
# Es el caso más grave: alguien levantó la mano y nadie respondió.
PUNTOS_SIN_CONTACTAR_MAS_DE_7_DIAS = 40
PUNTOS_SIN_CONTACTAR_3_A_7_DIAS = 30
PUNTOS_SIN_CONTACTAR_RECIENTE = 20

# ── Lead contactado pero sin seguimiento reciente ──
PUNTOS_SIN_SEGUIMIENTO_MAS_DE_14_DIAS = 30
PUNTOS_SIN_SEGUIMIENTO_7_A_14_DIAS = 20
PUNTOS_SIN_SEGUIMIENTO_3_A_7_DIAS = 10

# ── Interés demostrado en propiedades del catálogo ──
PUNTOS_CON_INTERES_ALTO = 20
PUNTOS_CON_INTERES = 10

# ── Etapa del embudo: (puntos, motivo) ──
# Un lead calificado que se enfría es la pérdida más cara.
ETAPAS = {
    "Calificado": (15, "Calificado, cerca del cierre"),
    "Contactado": (10, "En conversación"),
    "Nuevo": (5, "Recién ingresado"),
}

# ── Prioridad marcada a mano por el ejecutivo ──
# Solo suma cuando es Alta: Media y Baja no aportan para no ensuciar los motivos
# con información que no aporta nada.
PUNTOS_PRIORIDAD_MANUAL_ALTA = 15

# ── Cortes de categoría ──
UMBRAL_URGENTE = 60
UMBRAL_ALTA = 40
UMBRAL_NORMAL = 20

ESTADO_CERRADO = "Cerrado"
CATEGORIA_SIN_ACCION = "Sin acción"


def _dias_desde(fecha, ahora):
    """
    Días completos transcurridos desde una fecha.
    Devuelve None si no hay fecha, y nunca un valor negativo.
    """
    if fecha is None:
        return None
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return max(0, (ahora - fecha).days)


def calcular_prioridad(
    lead,
    ultima_interaccion=None,
    total_interacciones=0,
    total_intereses=0,
    tiene_interes_alto=False,
    ahora=None,
):
    """
    Calcula la prioridad de atención de un lead.

    Recibe el lead y los datos agregados de su actividad, que vienen precalculados
    desde una consulta agrupada. La función no consulta la base: así se puede
    priorizar una lista completa sin una consulta por lead.

    Parámetros:
        lead                 objeto Lead con estado, prioridad y fecha_creacion
        ultima_interaccion   fecha del último contacto, o None si nunca hubo
        total_interacciones  cantidad de contactos registrados
        total_intereses      cantidad de propiedades de interés
        tiene_interes_alto   si alguna de esas propiedades tiene interés Alto
        ahora                momento de referencia, útil para las pruebas

    Devuelve un diccionario con el puntaje, la categoría, los motivos y los datos
    de actividad que el frontend muestra en la tabla.
    """
    if ahora is None:
        ahora = datetime.now(timezone.utc)

    # Si nunca se lo contactó, el reloj corre desde que ingresó al sistema
    referencia = ultima_interaccion or lead.fecha_creacion
    dias = _dias_desde(referencia, ahora)
    if dias is None:
        dias = 0

    base = {
        "dias_sin_contacto": dias,
        "total_interacciones": total_interacciones,
        "total_intereses": total_intereses,
    }

    # Un lead cerrado ya no compite por la atención del ejecutivo
    if lead.estado == ESTADO_CERRADO:
        return {
            **base,
            "puntaje": 0,
            "categoria": CATEGORIA_SIN_ACCION,
            "motivos": ["El lead está cerrado"],
        }

    puntaje = 0
    motivos = []

    # 1. Antigüedad del último contacto
    if total_interacciones == 0:
        if dias > 7:
            puntaje += PUNTOS_SIN_CONTACTAR_MAS_DE_7_DIAS
            motivos.append(f"Nunca contactado, ingresó hace {dias} días")
        elif dias >= 3:
            puntaje += PUNTOS_SIN_CONTACTAR_3_A_7_DIAS
            motivos.append(f"Nunca contactado, ingresó hace {dias} días")
        else:
            puntaje += PUNTOS_SIN_CONTACTAR_RECIENTE
            motivos.append("Nunca contactado, ingresó hace poco")
    else:
        if dias > 14:
            puntaje += PUNTOS_SIN_SEGUIMIENTO_MAS_DE_14_DIAS
            motivos.append(f"{dias} días sin contacto")
        elif dias >= 7:
            puntaje += PUNTOS_SIN_SEGUIMIENTO_7_A_14_DIAS
            motivos.append(f"{dias} días sin contacto")
        elif dias >= 3:
            puntaje += PUNTOS_SIN_SEGUIMIENTO_3_A_7_DIAS
            motivos.append(f"{dias} días sin contacto")
        else:
            motivos.append("Contactado hace menos de 3 días")

    # 2. Interés demostrado en propiedades concretas
    if total_intereses > 0:
        etiqueta = "propiedad" if total_intereses == 1 else "propiedades"
        if tiene_interes_alto:
            puntaje += PUNTOS_CON_INTERES_ALTO
            motivos.append(f"{total_intereses} {etiqueta} de interés, una con interés alto")
        else:
            puntaje += PUNTOS_CON_INTERES
            motivos.append(f"{total_intereses} {etiqueta} de interés")

    # 3. Etapa del embudo
    puntos_etapa, motivo_etapa = ETAPAS.get(lead.estado, (0, None))
    if puntos_etapa:
        puntaje += puntos_etapa
        motivos.append(motivo_etapa)

    # 4. Prioridad marcada a mano
    if lead.prioridad == "Alta":
        puntaje += PUNTOS_PRIORIDAD_MANUAL_ALTA
        motivos.append("Marcado como prioridad alta")

    if puntaje >= UMBRAL_URGENTE:
        categoria = "Urgente"
    elif puntaje >= UMBRAL_ALTA:
        categoria = "Alta"
    elif puntaje >= UMBRAL_NORMAL:
        categoria = "Normal"
    else:
        categoria = "Baja"

    return {**base, "puntaje": puntaje, "categoria": categoria, "motivos": motivos}

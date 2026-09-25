"""
Registro de auditoría: deja constancia de quién hizo qué y cuándo.

Por qué el registro es explícito y no automático
------------------------------------------------
SQLAlchemy permite detectar automáticamente todo lo que se crea, modifica o borra
con un listener de sesión. Es más difícil de olvidar, pero acá produciría registros
falsos: el endpoint que lista tareas modifica fecha_limite para poder serializarla,
y un listener interpretaría esa lectura como una modificación real.

Un registro de auditoría con entradas falsas no sirve, porque su único valor es que
se pueda confiar en él. Por eso cada endpoint llama explícitamente a registrar(), y
el riesgo de olvidar uno se cubre con prueba_auditoria.py, que recorre todos los
endpoints de escritura y verifica que cada uno deje constancia. Si se agrega un
endpoint nuevo hay que sumarlo a esa prueba.

El registro se agrega a la misma sesión que la operación, sin hacer commit acá. De
esa forma la acción y su registro se guardan juntos o no se guarda ninguno: no puede
quedar una acción sin rastro ni un rastro de algo que no pasó.
"""

import models

# ── Acciones ──
CREAR = "crear"
ACTUALIZAR = "actualizar"
ELIMINAR = "eliminar"
GENERAR = "generar"

ACCIONES = (CREAR, ACTUALIZAR, ELIMINAR, GENERAR)

# ── Entidades ──
LEAD = "lead"
PROPIEDAD = "propiedad"
TAREA = "tarea"
INTERACCION = "interaccion"
INTERES = "interes"
ANALISIS = "analisis"
OPORTUNIDAD = "oportunidad"
VISITA = "visita"

ENTIDADES = (LEAD, PROPIEDAD, OPORTUNIDAD, VISITA, TAREA, INTERACCION, INTERES, ANALISIS)

# Campos que se comparan al actualizar, por entidad. Se listan explícitamente para
# no registrar columnas internas ni los campos calculados que se agregan al objeto.
CAMPOS_COMPARABLES = {
    LEAD: (
        "nombre", "email", "telefono", "estado", "prioridad", "tipo_operacion",
        "presupuesto_min", "presupuesto_max", "moneda", "comunas_interes",
        "tipo_propiedad_buscada", "dormitorios_min", "banos_min", "plazo_decision",
        "financiamiento", "origen", "proxima_accion", "fecha_proxima_accion", "es_demo",
    ),
    PROPIEDAD: ("titulo", "tipo", "precio", "direccion", "estado"),
    OPORTUNIDAD: (
        "lead_id", "propiedad_id", "tipo_operacion", "etapa", "valor_estimado",
        "moneda", "probabilidad", "fecha_cierre_estimada", "fecha_cierre",
        "motivo_cierre", "notas", "ejecutivo_id",
    ),
    VISITA: (
        "lead_id", "propiedad_id", "oportunidad_id", "ejecutivo_id", "fecha_hora",
        "duracion_minutos", "estado", "modalidad", "punto_encuentro", "resultado",
        "motivo_cancelacion", "proxima_accion",
    ),
    TAREA: ("titulo", "descripcion", "estado", "prioridad", "fecha_limite", "lead_id"),
}


def instantanea(objeto, entidad: str) -> dict:
    """
    Toma una foto de los campos comparables de un objeto.

    Se usa antes y después de actualizar para saber qué cambió realmente.
    """
    campos = CAMPOS_COMPARABLES.get(entidad, ())
    return {campo: getattr(objeto, campo, None) for campo in campos}


def resumir_cambios(antes: dict, despues: dict) -> str:
    """
    Describe en texto qué campos cambiaron entre dos instantáneas.

    Devuelve algo como "estado: Nuevo -> Contactado; prioridad: Media -> Alta".
    Si nada cambió lo dice, porque una petición que no modifica nada también es
    información: significa que alguien guardó sin cambios.
    """
    partes = []
    for campo, nuevo in despues.items():
        viejo = antes.get(campo)
        if viejo != nuevo:
            partes.append(f"{campo}: {_mostrar(viejo)} -> {_mostrar(nuevo)}")

    return "; ".join(partes) if partes else "sin cambios efectivos"


def _mostrar(valor) -> str:
    """Representa un valor para el texto del registro."""
    if valor is None or valor == "":
        return "vacío"
    return str(valor)


def registrar(
    db,
    usuario,
    accion: str,
    entidad: str,
    entidad_id=None,
    descripcion: str = None,
    detalle: str = None,
) -> models.Auditoria:
    """
    Agrega un registro de auditoría a la sesión actual.

    No hace commit: lo hace el endpoint junto con la operación que está registrando,
    para que ambas cosas queden en la misma transacción.

    Parámetros:
        usuario      quien ejecutó la acción; se guarda su id y su correo
        accion       crear, actualizar, eliminar o generar
        entidad      sobre qué tipo de registro se actuó
        entidad_id   id del registro afectado, si aplica
        descripcion  texto corto y legible de lo que ocurrió
        detalle      qué campos cambiaron, para las actualizaciones
    """
    registro = models.Auditoria(
        usuario_id=getattr(usuario, "id", None),
        usuario_email=getattr(usuario, "email", None),
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        descripcion=(descripcion or "")[:250] or None,
        detalle=detalle,
    )
    db.add(registro)
    return registro

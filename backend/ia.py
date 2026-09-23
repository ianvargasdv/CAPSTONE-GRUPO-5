"""
Integración con el modelo de lenguaje que genera los análisis del CRM.

Está implementado contra el formato de chat completions compatible con OpenAI, que
es el que exponen tanto los servicios pagos como los modelos que corren en local.
Eso permite cambiar de proveedor moviendo dos variables del .env, sin tocar código:

    IA_BASE_URL=https://api.del-proveedor.com/v1     (servicio alojado)
    IA_BASE_URL=http://localhost:11434/v1            (modelo local con Ollama)

Dos decisiones importantes:

1. La llamada se hace desde el backend, nunca desde el navegador. Si se hiciera
   desde el frontend la clave del proveedor viajaría al cliente y cualquiera podría
   leerla del código de la página.

2. El texto que se le envía al modelo se arma únicamente con registros que existen
   en la base. El modelo no consulta nada por su cuenta: solo reformula lo que se le
   entrega. Ese texto se guarda junto con la respuesta para poder revisar después
   con qué información se produjo cada análisis.

Se usa urllib de la biblioteca estándar en lugar de agregar una dependencia HTTP,
porque es una sola petición y así el proyecto no suma otra librería que instalar.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import timezone

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL = (os.getenv("IA_BASE_URL") or "").rstrip("/")
API_KEY = os.getenv("IA_API_KEY") or ""
MODELO = os.getenv("IA_MODELO") or ""
TIMEOUT_SEGUNDOS = int(os.getenv("IA_TIMEOUT_SEGUNDOS", "60"))

# Tope de tokens de la respuesta. Acota el costo máximo de cada llamada: el resumen
# son cuatro oraciones, así que 300 sobra y evita pagar una respuesta desbordada.
MAX_TOKENS = int(os.getenv("IA_MAX_TOKENS", "300"))

# Temperatura. Se deja configurable porque algunos modelos recientes rechazan el
# parámetro: dejando IA_TEMPERATURA vacío en el .env simplemente no se envía.
_TEMPERATURA_CRUDA = os.getenv("IA_TEMPERATURA", "0.2").strip()
TEMPERATURA = float(_TEMPERATURA_CRUDA) if _TEMPERATURA_CRUDA else None

# Límite de caracteres de la respuesta que se guarda, por si el modelo se extiende
MAX_CARACTERES_RESPUESTA = 4000


class IANoConfigurada(Exception):
    """Falta la configuración del proveedor en el .env."""


class IAFallo(Exception):
    """El proveedor no respondió o respondió algo que no se pudo interpretar."""


INSTRUCCIONES = """Eres un asistente para ejecutivos inmobiliarios. Recibes la ficha de un prospecto con su historial real registrado en el CRM y escribes un resumen breve para que el ejecutivo se ponga al día antes de contactarlo.

Reglas que debes seguir sin excepción:
- Usa únicamente la información que aparece en la ficha. No agregues datos, nombres, fechas, montos ni supuestos que no estén escritos.
- Si la ficha tiene poca información, dilo con claridad en lugar de rellenar.
- No inventes el motivo de compra, la situación económica ni las intenciones del cliente si no están registradas.
- Escribe en español de Chile, en tono profesional y directo.
- Máximo cuatro oraciones, en un solo párrafo. Sin títulos ni listas.
- Cierra indicando cuál sería el siguiente paso razonable según lo registrado."""


def esta_configurada() -> bool:
    """Indica si hay proveedor de IA configurado."""
    return bool(BASE_URL and MODELO)


def _sin_clave(texto: str) -> str:
    """
    Elimina la clave del texto en caso de que apareciera.

    La clave viaja en la cabecera Authorization, no en el cuerpo, así que no debería
    volver en ninguna respuesta. Esto es una red de contención: un mensaje de error
    que llega al navegador nunca puede contener la credencial.
    """
    if API_KEY and len(API_KEY) > 8:
        texto = texto.replace(API_KEY, "***")
    return texto


# Traducción de los códigos de respuesta a algo que el ejecutivo pueda entender
_MENSAJES_POR_ESTADO = {
    400: "El proveedor rechazó la petición, habitualmente por un parámetro que el modelo no acepta.",
    401: "El proveedor rechazó la clave de API. Revisa IA_API_KEY en el .env del backend.",
    403: "La clave no tiene permiso para usar este modelo.",
    404: "El proveedor no reconoce el modelo configurado. Revisa IA_MODELO en el .env del backend.",
}


def _describir_error_http(error: urllib.error.HTTPError) -> str:
    """
    Convierte un error del proveedor en un mensaje claro, sin datos sensibles.

    Se distinguen los casos que tienen soluciones distintas: clave inválida, modelo
    inexistente, falta de crédito y problemas temporales. Así el mensaje que ve el
    usuario dice qué hacer en lugar de mostrar un código suelto.
    """
    crudo = error.read().decode("utf-8", errors="replace")

    detalle = ""
    codigo = ""
    try:
        contenido = json.loads(crudo).get("error") or {}
        detalle = contenido.get("message") or ""
        codigo = contenido.get("code") or ""
    except (json.JSONDecodeError, AttributeError, TypeError):
        detalle = crudo[:200]

    if error.code == 429:
        if codigo == "insufficient_quota":
            mensaje = "La cuenta del proveedor no tiene crédito disponible."
        else:
            mensaje = "El proveedor está limitando la cantidad de llamadas. Espera unos segundos."
    elif error.code >= 500:
        mensaje = "El proveedor tuvo un problema temporal. Vuelve a intentar en un momento."
    else:
        mensaje = _MENSAJES_POR_ESTADO.get(
            error.code, f"El proveedor respondió con el código {error.code}."
        )

    if detalle:
        mensaje += f" Detalle del proveedor: {detalle[:200]}"

    return _sin_clave(mensaje)


def _fecha(valor) -> str:
    """Formatea una fecha para el texto del prompt."""
    if valor is None:
        return "sin fecha"
    if getattr(valor, "tzinfo", None) is None:
        return valor.strftime("%d-%m-%Y")
    return valor.astimezone(timezone.utc).strftime("%d-%m-%Y")


def construir_ficha(lead, interacciones, intereses, propiedades_por_id) -> str:
    """
    Arma el texto que se le envía al modelo a partir de los registros del lead.

    Se construye acá y no en el endpoint para que quede en un solo lugar revisable
    qué información sale del sistema hacia el proveedor.

    Parámetros:
        lead                  el lead, ya con su prioridad calculada
        interacciones         sus interacciones, de más reciente a más antigua
        intereses             sus propiedades de interés
        propiedades_por_id    diccionario id -> propiedad, para describir cada interés
    """
    lineas = [
        "FICHA DEL PROSPECTO",
        f"Nombre: {lead.nombre}",
        f"Estado en el embudo: {lead.estado}",
        f"Prioridad asignada: {lead.prioridad}",
        f"Fecha de ingreso: {_fecha(lead.fecha_creacion)}",
    ]

    # La prioridad la calcula prioridad.py y se adjunta al lead antes de llamar aquí
    categoria = getattr(lead, "categoria", None)
    if categoria:
        lineas.append(f"Nivel de atención calculado: {categoria} ({lead.puntaje} puntos)")
        motivos = getattr(lead, "motivos", None) or []
        if motivos:
            lineas.append(f"Motivos del cálculo: {'; '.join(motivos)}")

    lineas.append("")
    lineas.append("PROPIEDADES DE INTERÉS")
    if intereses:
        for interes in intereses:
            propiedad = propiedades_por_id.get(interes.propiedad_id)
            if propiedad:
                detalle = f"{propiedad.titulo} ({propiedad.tipo}, {propiedad.direccion}, precio {propiedad.precio})"
            else:
                detalle = f"propiedad {interes.propiedad_id}, ya no está en el catálogo"
            texto = f"- {detalle}. Nivel de interés: {interes.nivel_interes}"
            if interes.notas:
                texto += f". Nota: {interes.notas}"
            lineas.append(texto)
    else:
        lineas.append("- Ninguna registrada")

    lineas.append("")
    lineas.append("HISTORIAL DE CONTACTO")
    if interacciones:
        for interaccion in interacciones:
            texto = f"- {_fecha(interaccion.fecha_creacion)}, {interaccion.tipo}"
            if interaccion.notas:
                texto += f": {interaccion.notas}"
            lineas.append(texto)
    else:
        lineas.append("- Sin contactos registrados")

    return "\n".join(lineas)


def generar_resumen(ficha: str) -> tuple[str, str]:
    """
    Envía la ficha al modelo y devuelve (resumen, nombre del modelo).

    Lanza IANoConfigurada si falta la configuración e IAFallo si el proveedor no
    responde o responde algo inesperado.
    """
    if not esta_configurada():
        raise IANoConfigurada(
            "El servicio de IA no está configurado. Falta IA_BASE_URL o IA_MODELO en el .env"
        )

    peticion_json = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": INSTRUCCIONES},
            {"role": "user", "content": ficha},
        ],
        # max_completion_tokens y no max_tokens: este último quedó deprecado en la
        # API de chat completions y los modelos nuevos lo rechazan.
        "max_completion_tokens": MAX_TOKENS,
    }

    # Solo se envía si está configurada. Temperatura baja busca que el modelo
    # reformule los datos en lugar de ser creativo, pero varios modelos recientes
    # no aceptan el parámetro, así que se puede desactivar desde el .env.
    if TEMPERATURA is not None:
        peticion_json["temperature"] = TEMPERATURA

    cuerpo = json.dumps(peticion_json).encode("utf-8")

    peticion = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=cuerpo,
        method="POST",
        headers={
            "Content-Type": "application/json",
            # Los servicios alojados exigen la clave. Los modelos locales la ignoran
            # pero varios piden que la cabecera exista, así que se envía igual.
            "Authorization": f"Bearer {API_KEY or 'local'}",
        },
    )

    try:
        with urllib.request.urlopen(peticion, timeout=TIMEOUT_SEGUNDOS) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # No se reintenta a propósito: un reintento automático sobre un error de
        # cuota o de parámetro gastaría crédito sin resolver nada.
        raise IAFallo(_describir_error_http(error)) from error
    except urllib.error.URLError as error:
        raise IAFallo(
            _sin_clave(f"No se pudo conectar con el proveedor de IA: {error.reason}")
        ) from error
    except TimeoutError as error:
        raise IAFallo(f"El proveedor no respondió en {TIMEOUT_SEGUNDOS} segundos") from error
    except json.JSONDecodeError as error:
        raise IAFallo("El proveedor devolvió una respuesta que no es JSON válido") from error

    try:
        eleccion = datos["choices"][0]
        texto = eleccion["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise IAFallo("La respuesta del proveedor no tiene el formato esperado") from error

    texto = (texto or "").strip()

    if not texto:
        # Los modelos de razonamiento consumen tokens internos que cuentan contra
        # max_completion_tokens y no se devuelven. Si el tope se agota razonando, la
        # respuesta llega vacía con finish_reason "length". Sin este mensaje el error
        # parecería una falla del proveedor en lugar de un límite mal configurado.
        if eleccion.get("finish_reason") == "length":
            raise IAFallo(
                f"El modelo agotó el límite de {MAX_TOKENS} tokens antes de escribir el "
                "resumen. Sube IA_MAX_TOKENS en el .env del backend."
            )
        raise IAFallo("El proveedor devolvió un resumen vacío")

    # El modelo informado por el proveedor puede diferir del solicitado
    modelo_usado = datos.get("model") or MODELO

    return texto[:MAX_CARACTERES_RESPUESTA], modelo_usado

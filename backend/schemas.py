import re
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator
from datetime import date, datetime


# Valores que acepta el negocio. Mantenerlos en un solo lugar evita que cada
# endpoint interprete estados distintos y que entren datos que la interfaz no sabe
# representar.
EstadoLead = Literal["Nuevo", "Contactado", "Calificado", "Cerrado"]
Prioridad = Literal["Alta", "Media", "Baja"]
TipoPropiedad = Literal["Departamento", "Casa", "Terreno", "Oficina"]
EstadoPropiedad = Literal["Disponible", "Reservada", "Vendida"]
TipoInteraccion = Literal["Llamada", "Email", "Visita", "WhatsApp"]
EstadoTarea = Literal["Pendiente", "En Progreso", "Completada"]
NivelInteres = Literal["Alto", "Medio", "Bajo"]
TipoOperacion = Literal["Compra", "Arriendo"]
Moneda = Literal["UF", "CLP"]
PlazoDecision = Literal["Inmediato", "0-3 meses", "3-6 meses", "6-12 meses", "Sin definir"]
Financiamiento = Literal["Crédito preaprobado", "En evaluación", "Recursos propios", "Sin definir"]
OrigenLead = Literal[
    "Referido", "Portal inmobiliario", "Redes sociales", "Sitio web", "Llamada", "Otro", "Demo capstone"
]

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
Correo = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=5, max_length=150)]
Telefono = Annotated[str, StringConstraints(strip_whitespace=True, min_length=7, max_length=20)]
TextoCorto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TextoLargo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
Comunas = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=300)]

PATRON_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PATRON_TELEFONO = re.compile(r"^[+()\d\s-]+$")


def _validar_correo(valor: str) -> str:
    if not PATRON_CORREO.fullmatch(valor):
        raise ValueError("Ingresa un correo válido")
    return valor


def _validar_telefono(valor: Optional[str]) -> Optional[str]:
    if valor is not None and not PATRON_TELEFONO.fullmatch(valor):
        raise ValueError("El teléfono solo puede contener números, espacios, +, - y paréntesis")
    return valor


def _validar_fecha_iso(valor: Optional[str]) -> Optional[str]:
    if valor in (None, ""):
        return valor
    try:
        date.fromisoformat(valor)
    except ValueError as error:
        raise ValueError("La fecha debe tener el formato YYYY-MM-DD y ser válida") from error
    return valor


class LeadBase(BaseModel):
    nombre: Nombre
    email: Correo
    telefono: Optional[Telefono] = None
    estado: EstadoLead = "Nuevo"
    prioridad: Prioridad = "Media"
    tipo_operacion: Optional[TipoOperacion] = None
    presupuesto_min: Optional[int] = Field(default=None, ge=0, le=999_999_999_999)
    presupuesto_max: Optional[int] = Field(default=None, ge=0, le=999_999_999_999)
    moneda: Optional[Moneda] = None
    comunas_interes: Optional[Comunas] = None
    tipo_propiedad_buscada: Optional[TipoPropiedad] = None
    dormitorios_min: Optional[int] = Field(default=None, ge=0, le=20)
    banos_min: Optional[int] = Field(default=None, ge=0, le=20)
    plazo_decision: Optional[PlazoDecision] = None
    financiamiento: Optional[Financiamiento] = None
    origen: Optional[OrigenLead] = None
    proxima_accion: Optional[TextoCorto] = None
    fecha_proxima_accion: Optional[date] = None

    _correo_valido = field_validator("email")(_validar_correo)
    _telefono_valido = field_validator("telefono")(_validar_telefono)

    @model_validator(mode="after")
    def validar_rango_presupuesto(self):
        if (
            self.presupuesto_min is not None
            and self.presupuesto_max is not None
            and self.presupuesto_min > self.presupuesto_max
        ):
            raise ValueError("El presupuesto mínimo no puede superar el máximo")
        return self


class LeadCrear(LeadBase):
    """Esquema utilizado para recibir los datos de un nuevo lead al registrarlo."""
    pass


class LeadActualizar(BaseModel):
    """
    Esquema para actualizar un lead existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    # El valor por omisión permite omitir el campo; su tipo no acepta null cuando
    # el cliente lo envía explícitamente. telefono sí acepta null para poder borrarlo.
    nombre: Nombre = None
    email: Correo = None
    telefono: Optional[Telefono] = None
    estado: EstadoLead = None
    prioridad: Prioridad = None
    tipo_operacion: Optional[TipoOperacion] = None
    presupuesto_min: Optional[int] = Field(default=None, ge=0, le=999_999_999_999)
    presupuesto_max: Optional[int] = Field(default=None, ge=0, le=999_999_999_999)
    moneda: Optional[Moneda] = None
    comunas_interes: Optional[Comunas] = None
    tipo_propiedad_buscada: Optional[TipoPropiedad] = None
    dormitorios_min: Optional[int] = Field(default=None, ge=0, le=20)
    banos_min: Optional[int] = Field(default=None, ge=0, le=20)
    plazo_decision: Optional[PlazoDecision] = None
    financiamiento: Optional[Financiamiento] = None
    origen: Optional[OrigenLead] = None
    proxima_accion: Optional[TextoCorto] = None
    fecha_proxima_accion: Optional[date] = None

    _correo_valido = field_validator("email")(_validar_correo)
    _telefono_valido = field_validator("telefono")(_validar_telefono)


class LeadRespuesta(LeadBase):
    """
    Esquema de respuesta de un lead.

    Los últimos campos no existen en la tabla: los calcula el módulo de prioridad
    a partir de la actividad del lead y se agregan a la respuesta. Son opcionales
    para que el esquema siga siendo válido si alguna vez se responde sin ellos.
    """
    id: int
    fecha_creacion: Optional[datetime] = None
    ejecutivo_id: Optional[int] = None
    ejecutivo_nombre: Optional[str] = None
    es_demo: bool = False

    # Calculados, no almacenados
    puntaje: Optional[int] = None
    categoria: Optional[str] = None
    motivos: Optional[List[str]] = None
    dias_sin_contacto: Optional[int] = None
    total_interacciones: Optional[int] = None
    total_intereses: Optional[int] = None

    class Config:
        from_attributes = True


class PropiedadBase(BaseModel):
    titulo: TextoCorto
    tipo: TipoPropiedad = "Departamento"
    precio: int = Field(gt=0, le=999_999_999_999)
    direccion: TextoCorto
    estado: EstadoPropiedad = "Disponible"


class PropiedadCrear(PropiedadBase):
    """Esquema utilizado para registrar una nueva propiedad."""
    pass


class PropiedadActualizar(BaseModel):
    """
    Esquema para actualizar una propiedad existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    titulo: TextoCorto = None
    tipo: TipoPropiedad = None
    precio: Annotated[int, Field(gt=0, le=999_999_999_999)] = None
    direccion: TextoCorto = None
    estado: EstadoPropiedad = None


class PropiedadRespuesta(PropiedadBase):
    """Esquema utilizado para responder información de la propiedad."""
    id: int
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteraccionCrear(BaseModel):
    """
    Esquema para registrar una nueva interacción con un lead.
    Recibe el tipo de contacto y notas opcionales.
    El lead_id se obtiene de la URL, no del body.
    """
    tipo: TipoInteraccion
    notas: Optional[TextoLargo] = None


class InteraccionRespuesta(BaseModel):
    """
    Esquema de respuesta para una interacción.
    Incluye el id, lead_id, tipo, notas y fecha de registro.
    """
    id: int
    lead_id: int
    tipo: str
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True



class TareaCrear(BaseModel):
    """
    Esquema para registrar una nueva tarea.
    El lead_id y la fecha_limite son opcionales.
    """
    titulo: TextoCorto
    descripcion: Optional[TextoLargo] = None
    estado: EstadoTarea = "Pendiente"
    prioridad: Prioridad = "Media"
    fecha_limite: Optional[str] = None   # formato ISO: YYYY-MM-DD
    lead_id: Optional[int] = Field(default=None, gt=0)

    _fecha_valida = field_validator("fecha_limite")(_validar_fecha_iso)


class TareaActualizar(BaseModel):
    """
    Esquema para actualizar una tarea existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    titulo: TextoCorto = None
    descripcion: Optional[TextoLargo] = None
    estado: EstadoTarea = None
    prioridad: Prioridad = None
    fecha_limite: Optional[str] = None   # formato ISO: YYYY-MM-DD, enviar "" para limpiar
    lead_id: Optional[int] = Field(default=None, gt=0)

    _fecha_valida = field_validator("fecha_limite")(_validar_fecha_iso)


class TareaRespuesta(BaseModel):
    """
    Esquema de respuesta para una tarea.
    Incluye todos los campos más el id y la fecha de creación.

    fecha_limite se declara como date y no como str: Pydantic la serializa igual,
    como "YYYY-MM-DD", así que el frontend recibe exactamente lo mismo. Antes los
    endpoints convertían la fecha a texto sobre el objeto ORM para que el esquema la
    aceptara, y eso dejaba el atributo marcado como modificado en la sesión: si algo
    hacía commit después, SQLAlchemy intentaba guardar el texto en una columna de
    fecha. Declarar bien el tipo acá evita el problema en su origen.
    """
    id: int
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    prioridad: str
    fecha_limite: Optional[date] = None
    lead_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteresCrear(BaseModel):
    """
    Esquema para registrar el interés de un lead en una propiedad.
    El lead_id se obtiene de la URL, no del body.
    """
    propiedad_id: int = Field(gt=0)
    nivel_interes: NivelInteres = "Medio"
    notas: Optional[TextoLargo] = None


class InteresRespuesta(BaseModel):
    """
    Esquema de respuesta para un interés registrado.
    Devuelve el propiedad_id para que el frontend lo cruce con el catálogo que ya tiene cargado.
    """
    id: int
    lead_id: int
    propiedad_id: int
    nivel_interes: str
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioRespuesta(BaseModel):
    """
    Datos públicos de un usuario.

    No incluye password_hash a propósito: este esquema define lo que la API puede
    devolver, y el hash de la contraseña nunca debe salir del backend.
    """
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginPeticion(BaseModel):
    """Credenciales enviadas al iniciar sesión."""
    email: Correo
    password: str = Field(min_length=1, max_length=128)

    _correo_valido = field_validator("email")(_validar_correo)


class TokenRespuesta(BaseModel):
    """
    Respuesta del login. Devuelve el token junto con los datos del usuario
    para que el frontend no tenga que hacer una segunda llamada.
    """
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespuesta


class AnalisisRespuesta(BaseModel):
    """
    Análisis generado por el modelo de lenguaje.

    Incluye la entrada además de la salida para que se pueda revisar con qué
    información se produjo el resumen.
    """
    id: int
    lead_id: int
    usuario_id: Optional[int] = None
    tipo: str
    entrada: Optional[str] = None
    salida: str
    modelo: Optional[str] = None

    # Consumo del proveedor. Quedan en nulo en los análisis anteriores a que se
    # empezara a registrar, y si el proveedor no informa el consumo.
    tokens_entrada: Optional[int] = None
    tokens_salida: Optional[int] = None
    costo_estimado_usd: Optional[float] = None

    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class EstadoIARespuesta(BaseModel):
    """
    Indica si hay proveedor de IA configurado, para que la interfaz no ofrezca
    generar resúmenes cuando no se puede.
    """
    configurada: bool
    modelo: Optional[str] = None


class ConsumoAgrupado(BaseModel):
    """Consumo acumulado de un grupo: un tipo de análisis, un modelo o un día."""
    etiqueta: str
    cantidad: int
    tokens_entrada: int
    tokens_salida: int
    costo_usd: float


class ConfiguracionIA(BaseModel):
    """
    Configuración con la que está corriendo el servicio de IA.

    Se expone en el panel del administrador para poder verificar qué valores tiene
    cargados el proceso. Como la configuración se lee al arrancar, un cambio en el
    .env no tiene efecto hasta reiniciar, y sin esto había que adivinar si el
    servidor estaba usando los valores nuevos o los viejos.

    No incluye la clave del proveedor ni ningún otro dato sensible.
    """
    modelo: Optional[str] = None
    max_tokens: int
    precio_entrada_usd_millon: float
    precio_salida_usd_millon: float
    envia_temperatura: bool


class ConsumoIARespuesta(BaseModel):
    """
    Consumo del agente de IA, para que el administrador pueda seguir el gasto.

    Los totales solo consideran los análisis que tienen consumo registrado. Los
    generados antes de que se empezara a registrar se cuentan aparte en
    analisis_sin_consumo, para no dar a entender que salieron gratis.
    """
    total_analisis: int
    analisis_sin_consumo: int
    tokens_entrada: int
    tokens_salida: int
    costo_total_usd: float
    costo_promedio_usd: Optional[float] = None

    # Presupuesto declarado en la configuración, para calcular cuánto queda
    presupuesto_usd: Optional[float] = None
    porcentaje_usado: Optional[float] = None

    por_tipo: List[ConsumoAgrupado] = []
    por_modelo: List[ConsumoAgrupado] = []
    por_dia: List[ConsumoAgrupado] = []

    # Configuración efectiva del proceso, para poder verificarla sin adivinar
    configuracion: Optional[ConfiguracionIA] = None


class AuditoriaRespuesta(BaseModel):
    """Una entrada del registro de auditoría."""
    id: int
    usuario_id: Optional[int] = None
    usuario_email: Optional[str] = None
    accion: str
    entidad: str
    entidad_id: Optional[int] = None
    descripcion: Optional[str] = None
    detalle: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditoriaPagina(BaseModel):
    """
    Una página del registro de auditoría.

    El listado se pagina porque crece con cada acción del sistema: es la única tabla
    del proyecto que no tiene un tamaño acotado por la operación del negocio.
    """
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int
    registros: List[AuditoriaRespuesta] = []


class AuditoriaFiltros(BaseModel):
    """
    Valores disponibles para filtrar el registro de auditoría.

    Las entidades y las acciones las define el backend, así que se envían desde acá
    en vez de repetirlas en el frontend: si mañana se audita una entidad nueva, la
    interfaz la ofrece sin tocarla. La lista de usuarios es la de quienes realmente
    aparecen en el registro, no la de todas las cuentas.
    """
    entidades: List[str] = []
    acciones: List[str] = []
    usuarios: List[str] = []

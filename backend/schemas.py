from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class LeadBase(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    estado: Optional[str] = "Nuevo"
    prioridad: Optional[str] = "Media"


class LeadCrear(LeadBase):
    """Esquema utilizado para recibir los datos de un nuevo lead al registrarlo."""
    pass


class LeadActualizar(BaseModel):
    """
    Esquema para actualizar un lead existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None


class LeadRespuesta(LeadBase):
    """
    Esquema de respuesta de un lead.

    Los últimos campos no existen en la tabla: los calcula el módulo de prioridad
    a partir de la actividad del lead y se agregan a la respuesta. Son opcionales
    para que el esquema siga siendo válido si alguna vez se responde sin ellos.
    """
    id: int
    fecha_creacion: Optional[datetime] = None

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
    titulo: str
    tipo: Optional[str] = "Departamento"
    precio: int
    direccion: str
    estado: Optional[str] = "Disponible"


class PropiedadCrear(PropiedadBase):
    """Esquema utilizado para registrar una nueva propiedad."""
    pass


class PropiedadActualizar(BaseModel):
    """
    Esquema para actualizar una propiedad existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    titulo: Optional[str] = None
    tipo: Optional[str] = None
    precio: Optional[int] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None


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
    tipo: str
    notas: Optional[str] = None


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
    titulo: str
    descripcion: Optional[str] = None
    estado: Optional[str] = "Pendiente"
    prioridad: Optional[str] = "Media"
    fecha_limite: Optional[str] = None   # formato ISO: YYYY-MM-DD
    lead_id: Optional[int] = None


class TareaActualizar(BaseModel):
    """
    Esquema para actualizar una tarea existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    fecha_limite: Optional[str] = None   # formato ISO: YYYY-MM-DD, enviar "" para limpiar
    lead_id: Optional[int] = None


class TareaRespuesta(BaseModel):
    """
    Esquema de respuesta para una tarea.
    Incluye todos los campos más el id y la fecha de creación.
    """
    id: int
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    prioridad: str
    fecha_limite: Optional[str] = None
    lead_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteresCrear(BaseModel):
    """
    Esquema para registrar el interés de un lead en una propiedad.
    El lead_id se obtiene de la URL, no del body.
    """
    propiedad_id: int
    nivel_interes: Optional[str] = "Medio"
    notas: Optional[str] = None


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
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginPeticion(BaseModel):
    """Credenciales enviadas al iniciar sesión."""
    email: str
    password: str


class TokenRespuesta(BaseModel):
    """
    Respuesta del login. Devuelve el token junto con los datos del usuario
    para que el frontend no tenga que hacer una segunda llamada.
    """
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespuesta

from pydantic import BaseModel
from typing import Optional
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
    """Esquema utilizado para responder información del lead con su ID y fecha de creación."""
    id: int
    fecha_creacion: Optional[datetime] = None

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

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


class LeadRespuesta(LeadBase):
    """Esquema utilizado para responder información del lead con su ID y fecha de creación."""
    id: int
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True

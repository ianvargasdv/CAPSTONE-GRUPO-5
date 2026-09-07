from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base


class Lead(Base):
    """
    Modelo ORM que representa un Lead o prospecto de cliente en el sistema CRM.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    estado = Column(String(50), default="Nuevo")
    prioridad = Column(String(50), default="Media")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())


class Propiedad(Base):
    """
    Modelo ORM que representa una propiedad o inmueble en el sistema CRM.
    """
    __tablename__ = "propiedades"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    tipo = Column(String(50), default="Departamento")
    precio = Column(Integer, nullable=False)
    direccion = Column(String(200), nullable=False)
    estado = Column(String(50), default="Disponible")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())


class Interaccion(Base):
    """
    Modelo ORM que representa una interacción registrada con un lead.
    Permite llevar historial de contacto: llamadas, visitas, emails, etc.
    Cada interacción pertenece a un lead mediante clave foránea.
    """
    __tablename__ = "interacciones"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False)        # Llamada, Visita, Email, WhatsApp
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())


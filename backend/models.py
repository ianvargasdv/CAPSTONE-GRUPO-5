from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, UniqueConstraint
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



class Tarea(Base):
    """
    Modelo ORM que representa una tarea pendiente en el CRM.
    Permite al ejecutivo registrar trabajo a realizar, opcionalmente vinculado a un lead.
    """
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(50), default="Pendiente")       # Pendiente, En Progreso, Completada
    prioridad = Column(String(50), default="Media")        # Alta, Media, Baja
    fecha_limite = Column(Date, nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())


class Interes(Base):
    """
    Modelo ORM que representa el interés de un lead en una propiedad del catálogo.
    Tabla intermedia que relaciona leads con propiedades.
    La restricción de unicidad evita registrar dos veces la misma propiedad para un mismo lead.
    """
    __tablename__ = "intereses"
    __table_args__ = (
        UniqueConstraint("lead_id", "propiedad_id", name="uq_lead_propiedad"),
    )

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    propiedad_id = Column(Integer, ForeignKey("propiedades.id", ondelete="CASCADE"), nullable=False)
    nivel_interes = Column(String(50), default="Medio")   # Alto, Medio, Bajo
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

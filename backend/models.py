from sqlalchemy import Column, Integer, String, DateTime
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


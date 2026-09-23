from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from database import Base


class Usuario(Base):
    """
    Modelo ORM de los usuarios que acceden al sistema.

    La contraseña nunca se guarda en texto plano: solo se almacena su hash bcrypt.
    El campo activo permite dar de baja un acceso sin borrar el registro.

    Hay dos roles. El ejecutivo trabaja la cartera: leads, propiedades, tareas y el
    asistente. El admin además supervisa el sistema, incluido el gasto del agente de
    IA. No existe un rol para los clientes porque los clientes no acceden al CRM:
    se comunican con la inmobiliaria y sus datos los registra el ejecutivo.

    El valor por omisión es ejecutivo, que es el rol con menos permisos.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False, default="ejecutivo")
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())


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


class AnalisisIA(Base):
    """
    Modelo ORM que guarda cada análisis generado por el modelo de lenguaje.

    Se almacena tanto la entrada como la salida a propósito. Guardar solo la
    respuesta dejaría un texto sin forma de verificar de dónde salió; con la entrada
    registrada se puede revisar exactamente qué información se le entregó al modelo
    y comprobar que no agregó nada por su cuenta.

    Además sirve de caché: si no hubo actividad nueva, se puede mostrar el último
    análisis en lugar de volver a pedirlo y pagarlo.
    """
    __tablename__ = "analisis_ia"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    # Queda registrado quién lo pidió. Si el usuario se borra, el análisis se conserva.
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    tipo = Column(String(50), nullable=False, default="resumen")
    entrada = Column(Text, nullable=True)
    salida = Column(Text, nullable=False)
    modelo = Column(String(100), nullable=True)

    # Consumo informado por el proveedor. Quedan en nulo para los análisis generados
    # antes de que se empezara a registrar el consumo.
    tokens_entrada = Column(Integer, nullable=True)
    tokens_salida = Column(Integer, nullable=True)

    # Costo calculado al momento de generar el análisis, con los precios vigentes
    # entonces. Se guarda ya calculado para que cambiar de modelo o de precio más
    # adelante no altere el histórico de lo que realmente se gastó.
    costo_estimado_usd = Column(Float, nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

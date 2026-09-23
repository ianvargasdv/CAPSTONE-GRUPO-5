from datetime import date, datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case, func
from sqlalchemy.orm import Session

import database
import models
import prioridad
import schemas
import seguridad

# Crear las tablas definidas en los modelos si aún no existen
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Capstone API")

# Orígenes autorizados a consumir la API. Antes estaba en "*", que con
# autenticación deja de tener sentido: solo el frontend debe poder llamar.
# Al desplegar hay que agregar aquí el dominio de producción.
ORIGENES_PERMITIDOS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# allow_credentials queda en False porque el token viaja en la cabecera
# Authorization, no en cookies, así que no hacen falta credenciales de origen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════
# Routers
#
# router_auth: login público y consulta del perfil.
# router_privado: declara la dependencia de autenticación una sola vez, por lo
#   que todos sus endpoints exigen token. Cualquier endpoint que se agregue a
#   este router queda protegido por defecto, sin poder olvidarse.
# ══════════════════════════════════════════════════════════════

router_auth = APIRouter(prefix="/api/auth", tags=["Autenticación"])

router_privado = APIRouter(
    prefix="/api",
    dependencies=[Depends(seguridad.usuario_actual)],
)


def _credenciales_invalidas() -> HTTPException:
    """
    Mismo error para email inexistente, usuario inactivo y contraseña incorrecta.
    Diferenciarlos permitiría averiguar qué correos están registrados.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos",
    )


# ══════════════════════════════════════════════════════════════
# Estado del servicio (público)
# ══════════════════════════════════════════════════════════════


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend funcionando correctamente"}


# ══════════════════════════════════════════════════════════════
# Autenticación
# ══════════════════════════════════════════════════════════════


@router_auth.post("/login", response_model=schemas.TokenRespuesta)
def login(datos: schemas.LoginPeticion, db: Session = Depends(database.obtener_db)):
    """
    Valida las credenciales y devuelve un token de sesión junto con los datos
    del usuario. Los correos se comparan en minúsculas.
    """
    email = datos.email.strip().lower()
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()

    if usuario is None or not usuario.activo:
        # Se verifica contra un hash señuelo para que la respuesta tarde lo
        # mismo que con un usuario real y no se pueda deducir si existe
        seguridad.gastar_tiempo_de_verificacion(datos.password)
        raise _credenciales_invalidas()

    if not seguridad.verificar_password(datos.password, usuario.password_hash):
        raise _credenciales_invalidas()

    return schemas.TokenRespuesta(
        access_token=seguridad.crear_token(usuario.id),
        usuario=usuario,
    )


@router_auth.get("/yo", response_model=schemas.UsuarioRespuesta)
def perfil(usuario: models.Usuario = Depends(seguridad.usuario_actual)):
    """
    Devuelve el usuario dueño del token. El frontend lo usa al cargar la página
    para saber si la sesión guardada sigue siendo válida.
    """
    return usuario


# ══════════════════════════════════════════════════════════════
# Leads
# ══════════════════════════════════════════════════════════════


def _actividad_de_leads(db: Session, lead_ids=None):
    """
    Resume la actividad de los leads: fecha del último contacto, cantidad de
    interacciones, cantidad de propiedades de interés y si alguna es de interés alto.

    Son dos consultas agrupadas, no una por lead. La base está alojada de forma
    remota y cada consulta cuesta decenas de milisegundos, así que recorrer lead
    por lead haría que el listado tarde segundos. Con este enfoque el costo es el
    mismo con 5 leads que con 500.

    Si se pasa lead_ids, limita el cálculo a esos leads.
    """
    consulta_interacciones = db.query(
        models.Interaccion.lead_id,
        func.max(models.Interaccion.fecha_creacion).label("ultima"),
        func.count(models.Interaccion.id).label("total"),
    ).group_by(models.Interaccion.lead_id)

    consulta_intereses = db.query(
        models.Interes.lead_id,
        func.count(models.Interes.id).label("total"),
        func.sum(case((models.Interes.nivel_interes == "Alto", 1), else_=0)).label("altos"),
    ).group_by(models.Interes.lead_id)

    if lead_ids is not None:
        consulta_interacciones = consulta_interacciones.filter(models.Interaccion.lead_id.in_(lead_ids))
        consulta_intereses = consulta_intereses.filter(models.Interes.lead_id.in_(lead_ids))

    por_interacciones = {f.lead_id: (f.ultima, f.total) for f in consulta_interacciones.all()}
    por_intereses = {f.lead_id: (f.total, f.altos or 0) for f in consulta_intereses.all()}

    return por_interacciones, por_intereses


def _agregar_prioridad(lead, por_interacciones, por_intereses, ahora):
    """
    Calcula la prioridad de un lead y la adjunta al objeto.

    Los campos que se asignan no son columnas de la tabla, así que SQLAlchemy los
    ignora: viajan en la respuesta pero no se intentan guardar.
    """
    ultima, total_interacciones = por_interacciones.get(lead.id, (None, 0))
    total_intereses, intereses_altos = por_intereses.get(lead.id, (0, 0))

    resultado = prioridad.calcular_prioridad(
        lead,
        ultima_interaccion=ultima,
        total_interacciones=total_interacciones,
        total_intereses=total_intereses,
        tiene_interes_alto=intereses_altos > 0,
        ahora=ahora,
    )

    for campo, valor in resultado.items():
        setattr(lead, campo, valor)

    return lead


@router_privado.get("/leads", response_model=List[schemas.LeadRespuesta])
def listar_leads(db: Session = Depends(database.obtener_db)):
    """
    Obtiene todos los leads con su prioridad calculada, ordenados de mayor a menor
    puntaje: ese es el orden en que conviene trabajarlos.
    """
    leads = db.query(models.Lead).all()
    por_interacciones, por_intereses = _actividad_de_leads(db)
    ahora = datetime.now(timezone.utc)

    for lead in leads:
        _agregar_prioridad(lead, por_interacciones, por_intereses, ahora)

    leads.sort(key=lambda lead: lead.puntaje, reverse=True)
    return leads


@router_privado.post("/leads", response_model=schemas.LeadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_lead(lead: schemas.LeadCrear, db: Session = Depends(database.obtener_db)):
    """Registra un nuevo lead en la base de datos."""
    nuevo_lead = models.Lead(
        nombre=lead.nombre,
        email=lead.email,
        telefono=lead.telefono,
        estado=lead.estado,
        prioridad=lead.prioridad,
    )
    db.add(nuevo_lead)
    db.commit()
    db.refresh(nuevo_lead)

    # Un lead recién creado no tiene actividad, así que no hace falta consultarla
    _agregar_prioridad(nuevo_lead, {}, {}, datetime.now(timezone.utc))
    return nuevo_lead


@router_privado.put("/leads/{lead_id}", response_model=schemas.LeadRespuesta)
def actualizar_lead(lead_id: int, datos: schemas.LeadActualizar, db: Session = Depends(database.obtener_db)):
    """
    Actualiza los campos de un lead existente.
    Solo modifica los campos que se envíen en el cuerpo de la solicitud.
    Devuelve 404 si el lead no existe.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(lead, campo, valor)

    db.commit()
    db.refresh(lead)

    # Cambiar el estado o la prioridad altera el puntaje, así que se recalcula
    por_interacciones, por_intereses = _actividad_de_leads(db, [lead.id])
    _agregar_prioridad(lead, por_interacciones, por_intereses, datetime.now(timezone.utc))
    return lead


@router_privado.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lead(lead_id: int, db: Session = Depends(database.obtener_db)):
    """
    Elimina un lead por su ID.
    Devuelve 404 si el lead no existe.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    db.delete(lead)
    db.commit()


# ══════════════════════════════════════════════════════════════
# Propiedades
# ══════════════════════════════════════════════════════════════


@router_privado.get("/propiedades", response_model=List[schemas.PropiedadRespuesta])
def listar_propiedades(db: Session = Depends(database.obtener_db)):
    """Obtiene el catálogo de todas las propiedades registradas."""
    propiedades = db.query(models.Propiedad).all()
    return propiedades


@router_privado.post("/propiedades", response_model=schemas.PropiedadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_propiedad(propiedad: schemas.PropiedadCrear, db: Session = Depends(database.obtener_db)):
    """Registra una nueva propiedad en la base de datos."""
    nueva_propiedad = models.Propiedad(
        titulo=propiedad.titulo,
        tipo=propiedad.tipo,
        precio=propiedad.precio,
        direccion=propiedad.direccion,
        estado=propiedad.estado,
    )
    db.add(nueva_propiedad)
    db.commit()
    db.refresh(nueva_propiedad)
    return nueva_propiedad


@router_privado.put("/propiedades/{propiedad_id}", response_model=schemas.PropiedadRespuesta)
def actualizar_propiedad(propiedad_id: int, datos: schemas.PropiedadActualizar, db: Session = Depends(database.obtener_db)):
    """
    Actualiza los campos de una propiedad existente.
    Solo modifica los campos que se envíen en el cuerpo de la solicitud.
    Devuelve 404 si la propiedad no existe.
    """
    propiedad = db.query(models.Propiedad).filter(models.Propiedad.id == propiedad_id).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(propiedad, campo, valor)

    db.commit()
    db.refresh(propiedad)
    return propiedad


@router_privado.delete("/propiedades/{propiedad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_propiedad(propiedad_id: int, db: Session = Depends(database.obtener_db)):
    """
    Elimina una propiedad por su ID.
    Devuelve 404 si la propiedad no existe.
    """
    propiedad = db.query(models.Propiedad).filter(models.Propiedad.id == propiedad_id).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    db.delete(propiedad)
    db.commit()


# ══════════════════════════════════════════════════════════════
# Interacciones
# ══════════════════════════════════════════════════════════════


@router_privado.get("/leads/{lead_id}/interacciones", response_model=List[schemas.InteraccionRespuesta])
def listar_interacciones(lead_id: int, db: Session = Depends(database.obtener_db)):
    """
    Obtiene el historial de interacciones de un lead específico.
    Devuelve 404 si el lead no existe.
    Las interacciones se ordenan de más reciente a más antigua.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    interacciones = (
        db.query(models.Interaccion)
        .filter(models.Interaccion.lead_id == lead_id)
        .order_by(models.Interaccion.fecha_creacion.desc())
        .all()
    )
    return interacciones


@router_privado.post("/leads/{lead_id}/interacciones", response_model=schemas.InteraccionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_interaccion(lead_id: int, datos: schemas.InteraccionCrear, db: Session = Depends(database.obtener_db)):
    """
    Registra una nueva interacción para un lead.
    Devuelve 404 si el lead no existe.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    nueva_interaccion = models.Interaccion(
        lead_id=lead_id,
        tipo=datos.tipo,
        notas=datos.notas,
    )
    db.add(nueva_interaccion)
    db.commit()
    db.refresh(nueva_interaccion)
    return nueva_interaccion


# ══════════════════════════════════════════════════════════════
# Tareas
# ══════════════════════════════════════════════════════════════


@router_privado.get("/tareas", response_model=List[schemas.TareaRespuesta])
def listar_tareas(db: Session = Depends(database.obtener_db)):
    """
    Obtiene todas las tareas ordenadas por fecha de creación descendente.
    """
    tareas = db.query(models.Tarea).order_by(models.Tarea.fecha_creacion.desc()).all()
    # Convertir fecha_limite de date a string para que Pydantic lo serialice correctamente
    for tarea in tareas:
        if tarea.fecha_limite:
            tarea.fecha_limite = tarea.fecha_limite.isoformat()
    return tareas


@router_privado.post("/tareas", response_model=schemas.TareaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_tarea(datos: schemas.TareaCrear, db: Session = Depends(database.obtener_db)):
    """
    Registra una nueva tarea en la base de datos.
    Si se indica lead_id, verifica que el lead exista antes de asociarlo.
    """
    if datos.lead_id:
        lead = db.query(models.Lead).filter(models.Lead.id == datos.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")

    # Convertir fecha_limite de string ISO a objeto date si se proporcionó
    fecha_limite_obj = None
    if datos.fecha_limite:
        try:
            fecha_limite_obj = date.fromisoformat(datos.fecha_limite)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    nueva_tarea = models.Tarea(
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        estado=datos.estado,
        prioridad=datos.prioridad,
        fecha_limite=fecha_limite_obj,
        lead_id=datos.lead_id,
    )
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)

    if nueva_tarea.fecha_limite:
        nueva_tarea.fecha_limite = nueva_tarea.fecha_limite.isoformat()
    return nueva_tarea


@router_privado.put("/tareas/{tarea_id}", response_model=schemas.TareaRespuesta)
def actualizar_tarea(tarea_id: int, datos: schemas.TareaActualizar, db: Session = Depends(database.obtener_db)):
    """
    Actualiza los campos de una tarea existente.
    Solo modifica los campos enviados en el body.
    Devuelve 404 si la tarea no existe.
    """
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    campos = datos.model_dump(exclude_unset=True)

    # Tratar fecha_limite por separado para convertirla a objeto date
    if "fecha_limite" in campos:
        valor_fecha = campos.pop("fecha_limite")
        if valor_fecha:
            try:
                tarea.fecha_limite = date.fromisoformat(valor_fecha)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        else:
            tarea.fecha_limite = None

    for campo, valor in campos.items():
        setattr(tarea, campo, valor)

    db.commit()
    db.refresh(tarea)

    if tarea.fecha_limite:
        tarea.fecha_limite = tarea.fecha_limite.isoformat()
    return tarea


@router_privado.delete("/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(tarea_id: int, db: Session = Depends(database.obtener_db)):
    """
    Elimina una tarea por su ID.
    Devuelve 404 si la tarea no existe.
    """
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    db.delete(tarea)
    db.commit()


# ══════════════════════════════════════════════════════════════
# Propiedades de interés
# ══════════════════════════════════════════════════════════════


@router_privado.get("/leads/{lead_id}/intereses", response_model=List[schemas.InteresRespuesta])
def listar_intereses(lead_id: int, db: Session = Depends(database.obtener_db)):
    """
    Obtiene las propiedades en las que un lead mostró interés.
    Devuelve 404 si el lead no existe.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    intereses = (
        db.query(models.Interes)
        .filter(models.Interes.lead_id == lead_id)
        .order_by(models.Interes.fecha_creacion.desc())
        .all()
    )
    return intereses


@router_privado.post("/leads/{lead_id}/intereses", response_model=schemas.InteresRespuesta, status_code=status.HTTP_201_CREATED)
def crear_interes(lead_id: int, datos: schemas.InteresCrear, db: Session = Depends(database.obtener_db)):
    """
    Registra el interés de un lead en una propiedad del catálogo.
    Valida que el lead y la propiedad existan, y que el interés no esté ya registrado.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    propiedad = db.query(models.Propiedad).filter(models.Propiedad.id == datos.propiedad_id).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    # Evita duplicar la misma propiedad para el mismo lead
    existente = (
        db.query(models.Interes)
        .filter(
            models.Interes.lead_id == lead_id,
            models.Interes.propiedad_id == datos.propiedad_id,
        )
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Esta propiedad ya está registrada como interés del lead")

    nuevo_interes = models.Interes(
        lead_id=lead_id,
        propiedad_id=datos.propiedad_id,
        nivel_interes=datos.nivel_interes,
        notas=datos.notas,
    )
    db.add(nuevo_interes)
    db.commit()
    db.refresh(nuevo_interes)
    return nuevo_interes


@router_privado.delete("/intereses/{interes_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_interes(interes_id: int, db: Session = Depends(database.obtener_db)):
    """
    Quita un interés registrado por su ID.
    Devuelve 404 si el interés no existe.
    """
    interes = db.query(models.Interes).filter(models.Interes.id == interes_id).first()
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    db.delete(interes)
    db.commit()


# Los routers se registran al final, cuando ya tienen todos sus endpoints
app.include_router(router_auth)
app.include_router(router_privado)

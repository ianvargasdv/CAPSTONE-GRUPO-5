from datetime import date, datetime, time, timedelta, timezone
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case, func
from sqlalchemy.orm import Session

import auditoria
import database
import ia
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


def _buscar_lead_por_email(db: Session, email: str, excluir_id: Optional[int] = None):
    """Busca un correo sin distinguir mayúsculas y permite excluir el lead editado."""
    consulta = db.query(models.Lead).filter(func.lower(models.Lead.email) == email.lower())
    if excluir_id is not None:
        consulta = consulta.filter(models.Lead.id != excluir_id)
    return consulta.first()


def _agregar_ejecutivos(db: Session, leads):
    """Agrega el nombre del responsable sin hacer una consulta por cada lead."""
    ids = {lead.ejecutivo_id for lead in leads if lead.ejecutivo_id is not None}
    nombres = {}
    if ids:
        nombres = {
            usuario.id: usuario.nombre
            for usuario in db.query(models.Usuario).filter(models.Usuario.id.in_(ids)).all()
        }
    for lead in leads:
        lead.ejecutivo_nombre = nombres.get(lead.ejecutivo_id)


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
    _agregar_ejecutivos(db, leads)

    leads.sort(key=lambda lead: lead.puntaje, reverse=True)
    return leads


@router_privado.post("/leads", response_model=schemas.LeadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_lead(
    lead: schemas.LeadCrear,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Registra un nuevo lead en la base de datos.

    El flush antes del registro de auditoría es necesario porque el id lo asigna la
    base de datos y hace falta para dejar constancia de qué lead se creó. El commit
    posterior guarda el lead y su registro en la misma transacción.
    """
    if _buscar_lead_por_email(db, lead.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un lead registrado con ese correo",
        )

    nuevo_lead = models.Lead(**lead.model_dump(), ejecutivo_id=usuario.id)
    db.add(nuevo_lead)
    db.flush()

    auditoria.registrar(
        db,
        usuario,
        auditoria.CREAR,
        auditoria.LEAD,
        nuevo_lead.id,
        f"Creó el lead {nuevo_lead.nombre}",
    )

    db.commit()
    db.refresh(nuevo_lead)

    # Un lead recién creado no tiene actividad, así que no hace falta consultarla
    _agregar_prioridad(nuevo_lead, {}, {}, datetime.now(timezone.utc))
    nuevo_lead.ejecutivo_nombre = usuario.nombre
    return nuevo_lead


@router_privado.put("/leads/{lead_id}", response_model=schemas.LeadRespuesta)
def actualizar_lead(
    lead_id: int,
    datos: schemas.LeadActualizar,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Actualiza los campos de un lead existente.
    Solo modifica los campos que se envíen en el cuerpo de la solicitud.
    Devuelve 404 si el lead no existe.

    Se toma una instantánea antes y después de aplicar los cambios para registrar
    qué campos se modificaron de verdad, no los que venían en la petición.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    antes = auditoria.instantanea(lead, auditoria.LEAD)
    campos = datos.model_dump(exclude_unset=True)

    if "email" in campos and _buscar_lead_por_email(db, campos["email"], excluir_id=lead.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe otro lead registrado con ese correo",
        )

    # En una actualización parcial puede venir solo uno de los límites. Se combina
    # con el valor que ya existe antes de validar el rango completo.
    presupuesto_min = campos.get("presupuesto_min", lead.presupuesto_min)
    presupuesto_max = campos.get("presupuesto_max", lead.presupuesto_max)
    if (
        presupuesto_min is not None
        and presupuesto_max is not None
        and presupuesto_min > presupuesto_max
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El presupuesto mínimo no puede superar el máximo",
        )

    for campo, valor in campos.items():
        setattr(lead, campo, valor)

    auditoria.registrar(
        db,
        usuario,
        auditoria.ACTUALIZAR,
        auditoria.LEAD,
        lead.id,
        f"Actualizó el lead {lead.nombre}",
        auditoria.resumir_cambios(antes, auditoria.instantanea(lead, auditoria.LEAD)),
    )

    db.commit()
    db.refresh(lead)

    # Cambiar el estado o la prioridad altera el puntaje, así que se recalcula
    por_interacciones, por_intereses = _actividad_de_leads(db, [lead.id])
    _agregar_prioridad(lead, por_interacciones, por_intereses, datetime.now(timezone.utc))
    _agregar_ejecutivos(db, [lead])
    return lead


@router_privado.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lead(
    lead_id: int,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Elimina un lead por su ID.
    Devuelve 404 si el lead no existe.

    El nombre se guarda en una variable antes de borrar: después de db.delete el
    objeto queda inutilizable y el registro tiene que decir qué se borró, porque la
    fila ya no existe para consultarla.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    nombre = lead.nombre

    db.delete(lead)

    auditoria.registrar(
        db,
        usuario,
        auditoria.ELIMINAR,
        auditoria.LEAD,
        lead_id,
        f"Eliminó el lead {nombre}",
    )

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
def crear_propiedad(
    propiedad: schemas.PropiedadCrear,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """Registra una nueva propiedad en la base de datos."""
    nueva_propiedad = models.Propiedad(
        titulo=propiedad.titulo,
        tipo=propiedad.tipo,
        precio=propiedad.precio,
        direccion=propiedad.direccion,
        estado=propiedad.estado,
    )
    db.add(nueva_propiedad)
    db.flush()

    auditoria.registrar(
        db,
        usuario,
        auditoria.CREAR,
        auditoria.PROPIEDAD,
        nueva_propiedad.id,
        f"Creó la propiedad {nueva_propiedad.titulo}",
    )

    db.commit()
    db.refresh(nueva_propiedad)
    return nueva_propiedad


@router_privado.put("/propiedades/{propiedad_id}", response_model=schemas.PropiedadRespuesta)
def actualizar_propiedad(
    propiedad_id: int,
    datos: schemas.PropiedadActualizar,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Actualiza los campos de una propiedad existente.
    Solo modifica los campos que se envíen en el cuerpo de la solicitud.
    Devuelve 404 si la propiedad no existe.
    """
    propiedad = db.query(models.Propiedad).filter(models.Propiedad.id == propiedad_id).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    antes = auditoria.instantanea(propiedad, auditoria.PROPIEDAD)

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(propiedad, campo, valor)

    auditoria.registrar(
        db,
        usuario,
        auditoria.ACTUALIZAR,
        auditoria.PROPIEDAD,
        propiedad.id,
        f"Actualizó la propiedad {propiedad.titulo}",
        auditoria.resumir_cambios(antes, auditoria.instantanea(propiedad, auditoria.PROPIEDAD)),
    )

    db.commit()
    db.refresh(propiedad)
    return propiedad


@router_privado.delete("/propiedades/{propiedad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_propiedad(
    propiedad_id: int,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Elimina una propiedad por su ID.
    Devuelve 404 si la propiedad no existe.
    """
    propiedad = db.query(models.Propiedad).filter(models.Propiedad.id == propiedad_id).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    titulo = propiedad.titulo

    db.delete(propiedad)

    auditoria.registrar(
        db,
        usuario,
        auditoria.ELIMINAR,
        auditoria.PROPIEDAD,
        propiedad_id,
        f"Eliminó la propiedad {titulo}",
    )

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
def crear_interaccion(
    lead_id: int,
    datos: schemas.InteraccionCrear,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Registra una nueva interacción para un lead.
    Devuelve 404 si el lead no existe.

    El registro de auditoría menciona al lead y no solo el id de la interacción,
    porque una interacción sin su lead no se entiende al leer el historial.
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
    db.flush()

    auditoria.registrar(
        db,
        usuario,
        auditoria.CREAR,
        auditoria.INTERACCION,
        nueva_interaccion.id,
        f"Registró una interacción de tipo {datos.tipo} con el lead {lead.nombre}",
    )

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
    return db.query(models.Tarea).order_by(models.Tarea.fecha_creacion.desc()).all()


@router_privado.post("/tareas", response_model=schemas.TareaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    datos: schemas.TareaCrear,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
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
    db.flush()

    auditoria.registrar(
        db,
        usuario,
        auditoria.CREAR,
        auditoria.TAREA,
        nueva_tarea.id,
        f"Creó la tarea {nueva_tarea.titulo}",
    )

    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea


@router_privado.put("/tareas/{tarea_id}", response_model=schemas.TareaRespuesta)
def actualizar_tarea(
    tarea_id: int,
    datos: schemas.TareaActualizar,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Actualiza los campos de una tarea existente.
    Solo modifica los campos enviados en el body.
    Devuelve 404 si la tarea no existe.
    """
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    antes = auditoria.instantanea(tarea, auditoria.TAREA)

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

    auditoria.registrar(
        db,
        usuario,
        auditoria.ACTUALIZAR,
        auditoria.TAREA,
        tarea.id,
        f"Actualizó la tarea {tarea.titulo}",
        auditoria.resumir_cambios(antes, auditoria.instantanea(tarea, auditoria.TAREA)),
    )

    db.commit()
    db.refresh(tarea)
    return tarea


@router_privado.delete("/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(
    tarea_id: int,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Elimina una tarea por su ID.
    Devuelve 404 si la tarea no existe.
    """
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    titulo = tarea.titulo

    db.delete(tarea)

    auditoria.registrar(
        db,
        usuario,
        auditoria.ELIMINAR,
        auditoria.TAREA,
        tarea_id,
        f"Eliminó la tarea {titulo}",
    )

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
def crear_interes(
    lead_id: int,
    datos: schemas.InteresCrear,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
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
    db.flush()

    auditoria.registrar(
        db,
        usuario,
        auditoria.CREAR,
        auditoria.INTERES,
        nuevo_interes.id,
        f"Vinculó la propiedad {propiedad.titulo} al lead {lead.nombre} con interés {datos.nivel_interes}",
    )

    db.commit()
    db.refresh(nuevo_interes)
    return nuevo_interes


@router_privado.delete("/intereses/{interes_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_interes(
    interes_id: int,
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Quita un interés registrado por su ID.
    Devuelve 404 si el interés no existe.

    Se consultan el lead y la propiedad para que el registro diga qué vínculo se
    deshizo. Con solo los ids el historial quedaría ilegible, y son dos consultas
    sobre una operación que no es frecuente.
    """
    interes = db.query(models.Interes).filter(models.Interes.id == interes_id).first()
    if not interes:
        raise HTTPException(status_code=404, detail="Interés no encontrado")

    lead = db.query(models.Lead).filter(models.Lead.id == interes.lead_id).first()
    propiedad = db.query(models.Propiedad).filter(models.Propiedad.id == interes.propiedad_id).first()

    nombre_lead = lead.nombre if lead else f"lead {interes.lead_id}"
    titulo_propiedad = propiedad.titulo if propiedad else f"propiedad {interes.propiedad_id}"

    db.delete(interes)

    auditoria.registrar(
        db,
        usuario,
        auditoria.ELIMINAR,
        auditoria.INTERES,
        interes_id,
        f"Quitó la propiedad {titulo_propiedad} de los intereses del lead {nombre_lead}",
    )

    db.commit()


# ══════════════════════════════════════════════════════════════
# Análisis con IA
# ══════════════════════════════════════════════════════════════


@router_privado.get("/ia/estado", response_model=schemas.EstadoIARespuesta)
def estado_ia():
    """
    Informa si hay proveedor de IA configurado, para que la interfaz no ofrezca
    generar resúmenes cuando no es posible.
    """
    configurada = ia.esta_configurada()
    return schemas.EstadoIARespuesta(
        configurada=configurada,
        modelo=ia.MODELO if configurada else None,
    )


def _agrupar_consumo(db: Session, columna, etiqueta_por_defecto: str = "sin dato"):
    """
    Agrupa el consumo de los análisis por la columna indicada.

    Una sola consulta agregada por agrupación, en lugar de traer todos los análisis
    y sumarlos en Python. Solo cuenta los que tienen consumo registrado.
    """
    filas = (
        db.query(
            columna.label("etiqueta"),
            func.count(models.AnalisisIA.id).label("cantidad"),
            func.coalesce(func.sum(models.AnalisisIA.tokens_entrada), 0).label("entrada"),
            func.coalesce(func.sum(models.AnalisisIA.tokens_salida), 0).label("salida"),
            func.coalesce(func.sum(models.AnalisisIA.costo_estimado_usd), 0.0).label("costo"),
        )
        .filter(models.AnalisisIA.costo_estimado_usd.isnot(None))
        .group_by(columna)
        .order_by(columna)
        .all()
    )

    return [
        schemas.ConsumoAgrupado(
            etiqueta=str(f.etiqueta) if f.etiqueta is not None else etiqueta_por_defecto,
            cantidad=f.cantidad,
            tokens_entrada=int(f.entrada),
            tokens_salida=int(f.salida),
            costo_usd=float(f.costo),
        )
        for f in filas
    ]


@router_privado.get("/ia/consumo", response_model=schemas.ConsumoIARespuesta)
def consumo_ia(
    db: Session = Depends(database.obtener_db),
    _admin: models.Usuario = Depends(seguridad.solo_admin),
):
    """
    Consumo acumulado del agente de IA. Reservado al rol admin.

    Devuelve el total gastado, el desglose por tipo de análisis, por modelo y por
    día, y qué porcentaje del presupuesto declarado se usó.

    Los análisis sin consumo registrado se informan por separado en lugar de contarse
    como gasto cero: son los que se generaron antes de que se empezara a registrar.
    """
    totales = db.query(
        func.count(models.AnalisisIA.id).label("cantidad"),
        func.coalesce(func.sum(models.AnalisisIA.tokens_entrada), 0).label("entrada"),
        func.coalesce(func.sum(models.AnalisisIA.tokens_salida), 0).label("salida"),
        func.coalesce(func.sum(models.AnalisisIA.costo_estimado_usd), 0.0).label("costo"),
    ).filter(models.AnalisisIA.costo_estimado_usd.isnot(None)).one()

    sin_consumo = (
        db.query(func.count(models.AnalisisIA.id))
        .filter(models.AnalisisIA.costo_estimado_usd.is_(None))
        .scalar()
    )

    cantidad = int(totales.cantidad)
    costo_total = float(totales.costo)

    promedio = costo_total / cantidad if cantidad else None

    porcentaje = None
    if ia.PRESUPUESTO_USD:
        porcentaje = costo_total / ia.PRESUPUESTO_USD * 100

    return schemas.ConsumoIARespuesta(
        total_analisis=cantidad,
        analisis_sin_consumo=int(sin_consumo or 0),
        tokens_entrada=int(totales.entrada),
        tokens_salida=int(totales.salida),
        costo_total_usd=costo_total,
        costo_promedio_usd=promedio,
        presupuesto_usd=ia.PRESUPUESTO_USD,
        configuracion=schemas.ConfiguracionIA(
            modelo=ia.MODELO or None,
            max_tokens=ia.MAX_TOKENS,
            precio_entrada_usd_millon=ia.PRECIO_ENTRADA_POR_MILLON,
            precio_salida_usd_millon=ia.PRECIO_SALIDA_POR_MILLON,
            envia_temperatura=ia.TEMPERATURA is not None,
        ),
        porcentaje_usado=porcentaje,
        por_tipo=_agrupar_consumo(db, models.AnalisisIA.tipo),
        por_modelo=_agrupar_consumo(db, models.AnalisisIA.modelo, "sin modelo"),
        por_dia=_agrupar_consumo(db, func.date(models.AnalisisIA.fecha_creacion)),
    )


@router_privado.get("/leads/{lead_id}/analisis", response_model=List[schemas.AnalisisRespuesta])
def listar_analisis(lead_id: int, db: Session = Depends(database.obtener_db)):
    """
    Devuelve los análisis generados para un lead, del más reciente al más antiguo.
    """
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    return (
        db.query(models.AnalisisIA)
        .filter(models.AnalisisIA.lead_id == lead_id)
        .order_by(models.AnalisisIA.fecha_creacion.desc())
        .all()
    )


@router_privado.post(
    "/leads/{lead_id}/analisis",
    response_model=schemas.AnalisisRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_analisis(
    lead_id: int,
    tipo: Literal["resumen", "recomendacion"] = "resumen",
    db: Session = Depends(database.obtener_db),
    usuario: models.Usuario = Depends(seguridad.usuario_actual),
):
    """
    Genera un análisis del lead con el modelo de lenguaje y lo guarda.

    El tipo define qué se pide: "resumen" describe la situación del prospecto y
    "recomendacion" propone la siguiente acción. Ambos parten de la misma ficha.
    FastAPI valida el valor contra los dos permitidos.

    Reúne los datos del lead, su prioridad calculada, sus propiedades de interés, su
    historial de contacto y sus tareas pendientes, arma con eso un texto y se lo
    envía al modelo. Queda registrado qué se envió, qué respondió, con qué modelo y
    quién lo pidió.

    El router ya exige autenticación; acá se pide además el usuario porque hace
    falta saber quién solicitó el análisis.

    Es una función sincrónica que puede tardar varios segundos. FastAPI ejecuta este
    tipo de endpoint en un hilo aparte, así que la espera no bloquea al resto.
    """
    if not ia.esta_configurada():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está configurado. Revisa IA_BASE_URL e IA_MODELO en el archivo .env del backend.",
        )

    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    # La prioridad y sus motivos forman parte del contexto que recibe el modelo
    por_interacciones, por_intereses = _actividad_de_leads(db, [lead.id])
    _agregar_prioridad(lead, por_interacciones, por_intereses, datetime.now(timezone.utc))

    interacciones = (
        db.query(models.Interaccion)
        .filter(models.Interaccion.lead_id == lead_id)
        .order_by(models.Interaccion.fecha_creacion.desc())
        .all()
    )

    intereses = db.query(models.Interes).filter(models.Interes.lead_id == lead_id).all()

    # Una sola consulta para todas las propiedades referenciadas
    propiedades_por_id = {}
    if intereses:
        ids = [i.propiedad_id for i in intereses]
        propiedades_por_id = {
            p.id: p for p in db.query(models.Propiedad).filter(models.Propiedad.id.in_(ids)).all()
        }

    # Solo las tareas sin completar: sirven para que la recomendación no proponga
    # algo que el ejecutivo ya tiene agendado
    tareas = (
        db.query(models.Tarea)
        .filter(models.Tarea.lead_id == lead_id, models.Tarea.estado != "Completada")
        .all()
    )

    # La ficha interpola la fecha en un texto, así que el objeto date se escribe
    # igual que antes ("vence el 2026-09-20") sin tener que convertirlo a mano
    ficha = ia.construir_ficha(lead, interacciones, intereses, propiedades_por_id, tareas)

    try:
        resultado = ia.generar_analisis(ficha, tipo)
    except ia.IANoConfigurada as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    except ia.IAFallo as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error))

    analisis = models.AnalisisIA(
        lead_id=lead_id,
        usuario_id=usuario.id,
        tipo=tipo,
        entrada=ficha,
        salida=resultado["texto"],
        modelo=resultado["modelo"],
        tokens_entrada=resultado["tokens_entrada"],
        tokens_salida=resultado["tokens_salida"],
        costo_estimado_usd=resultado["costo_estimado_usd"],
    )
    db.add(analisis)
    db.flush()

    # El costo va en el registro porque la generación es la única acción del sistema
    # que cuesta dinero: interesa saber quién la pidió y cuánto salió.
    costo = resultado["costo_estimado_usd"]
    detalle_costo = f"{costo:.6f} USD" if costo is not None else "costo no informado"

    auditoria.registrar(
        db,
        usuario,
        auditoria.GENERAR,
        auditoria.ANALISIS,
        analisis.id,
        f"Generó un análisis de tipo {tipo} para el lead {lead.nombre}",
        f"modelo: {resultado['modelo']}; costo estimado: {detalle_costo}",
    )

    db.commit()
    db.refresh(analisis)
    return analisis


def _fecha_o_400(valor: str, nombre: str) -> date:
    """
    Convierte un texto YYYY-MM-DD a fecha, o devuelve 400 si no tiene ese formato.

    Un filtro con formato inválido es un error de quien llama, no un motivo para
    ignorar el filtro y devolver más datos de los pedidos.
    """
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"El parámetro '{nombre}' debe tener el formato YYYY-MM-DD",
        )


# ══════════════════════════════════════════════════════════════
# Auditoría
#
# Reservada al rol admin. Un ejecutivo no debe poder revisar lo que hacen sus
# compañeros, y menos aún consultar el registro de sus propias acciones para
# saber qué queda grabado.
# ══════════════════════════════════════════════════════════════


@router_privado.get("/auditoria/filtros", response_model=schemas.AuditoriaFiltros)
def filtros_auditoria(
    db: Session = Depends(database.obtener_db),
    _admin: models.Usuario = Depends(seguridad.solo_admin),
):
    """
    Valores que la interfaz ofrece en los selectores de filtro.

    Se declara antes que /auditoria/{nada} para evitar ambigüedades de ruta y se
    consulta una sola vez al abrir la vista.
    """
    correos = (
        db.query(models.Auditoria.usuario_email)
        .filter(models.Auditoria.usuario_email.isnot(None))
        .distinct()
        .order_by(models.Auditoria.usuario_email)
        .all()
    )

    return schemas.AuditoriaFiltros(
        entidades=list(auditoria.ENTIDADES),
        acciones=list(auditoria.ACCIONES),
        usuarios=[fila[0] for fila in correos],
    )


@router_privado.get("/auditoria", response_model=schemas.AuditoriaPagina)
def listar_auditoria(
    pagina: int = Query(1, ge=1, description="Número de página, empezando en 1"),
    por_pagina: int = Query(25, ge=1, le=100, description="Registros por página"),
    usuario_email: Optional[str] = None,
    entidad: Optional[str] = None,
    accion: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    busqueda: Optional[str] = None,
    db: Session = Depends(database.obtener_db),
    _admin: models.Usuario = Depends(seguridad.solo_admin),
):
    """
    Devuelve el registro de auditoría paginado y filtrado. Reservado al rol admin.

    Se pagina porque es la única tabla del proyecto sin un tamaño acotado por la
    operación del negocio: crece con cada acción y a los meses tiene miles de filas.
    El tope de 100 por página lo impone el propio endpoint, para que un parámetro
    demasiado grande no se convierta en una consulta que traiga la tabla completa.

    Las fechas se interpretan como días completos en UTC, que es la zona en que se
    guardan. Con horario chileno el corte puede caer unas horas antes de la
    medianoche local; es aceptable para filtrar por día y evita convertir zonas.
    """
    consulta = db.query(models.Auditoria)

    if usuario_email:
        consulta = consulta.filter(models.Auditoria.usuario_email == usuario_email)

    if entidad:
        # Se valida contra la lista del módulo de auditoría en lugar de usar Literal
        # para no tener que repetir los valores en la firma del endpoint
        if entidad not in auditoria.ENTIDADES:
            raise HTTPException(
                status_code=400,
                detail=f"Entidad desconocida. Valores válidos: {', '.join(auditoria.ENTIDADES)}",
            )
        consulta = consulta.filter(models.Auditoria.entidad == entidad)

    if accion:
        if accion not in auditoria.ACCIONES:
            raise HTTPException(
                status_code=400,
                detail=f"Acción desconocida. Valores válidos: {', '.join(auditoria.ACCIONES)}",
            )
        consulta = consulta.filter(models.Auditoria.accion == accion)

    if desde:
        inicio = _fecha_o_400(desde, "desde")
        consulta = consulta.filter(
            models.Auditoria.fecha_creacion >= datetime.combine(inicio, time.min, tzinfo=timezone.utc)
        )

    if hasta:
        # Se suma un día y se compara con menor estricto para incluir el día completo:
        # con <= la medianoche dejaría fuera todo lo ocurrido durante esa jornada
        fin = _fecha_o_400(hasta, "hasta") + timedelta(days=1)
        consulta = consulta.filter(
            models.Auditoria.fecha_creacion < datetime.combine(fin, time.min, tzinfo=timezone.utc)
        )

    if busqueda:
        texto = f"%{busqueda.strip()}%"
        consulta = consulta.filter(models.Auditoria.descripcion.ilike(texto))

    # El total se calcula sobre la consulta ya filtrada y antes de paginar, para que
    # la interfaz sepa cuántas páginas hay realmente
    total = consulta.count()

    registros = (
        consulta.order_by(models.Auditoria.fecha_creacion.desc(), models.Auditoria.id.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
        .all()
    )

    total_paginas = (total + por_pagina - 1) // por_pagina

    return schemas.AuditoriaPagina(
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        total_paginas=total_paginas,
        registros=registros,
    )


# Los routers se registran al final, cuando ya tienen todos sus endpoints
app.include_router(router_auth)
app.include_router(router_privado)

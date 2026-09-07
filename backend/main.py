from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import database
import models
import schemas

# Crear las tablas definidas en los modelos si aún no existen
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Capstone API")

# Configuración de CORS para permitir solicitudes desde el frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend funcionando correctamente"}


@app.get("/api/leads", response_model=List[schemas.LeadRespuesta])
def listar_leads(db: Session = Depends(database.obtener_db)):
    """Obtiene la lista de todos los leads registrados."""
    leads = db.query(models.Lead).all()
    return leads


@app.post("/api/leads", response_model=schemas.LeadRespuesta, status_code=status.HTTP_201_CREATED)
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
    return nuevo_lead


@app.put("/api/leads/{lead_id}", response_model=schemas.LeadRespuesta)
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
    return lead


@app.delete("/api/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@app.get("/api/propiedades", response_model=List[schemas.PropiedadRespuesta])
def listar_propiedades(db: Session = Depends(database.obtener_db)):
    """Obtiene el catálogo de todas las propiedades registradas."""
    propiedades = db.query(models.Propiedad).all()
    return propiedades


@app.post("/api/propiedades", response_model=schemas.PropiedadRespuesta, status_code=status.HTTP_201_CREATED)
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


@app.put("/api/propiedades/{propiedad_id}", response_model=schemas.PropiedadRespuesta)
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


@app.delete("/api/propiedades/{propiedad_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@app.get("/api/leads/{lead_id}/interacciones", response_model=List[schemas.InteraccionRespuesta])
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


@app.post("/api/leads/{lead_id}/interacciones", response_model=schemas.InteraccionRespuesta, status_code=status.HTTP_201_CREATED)
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




@app.get("/api/tareas", response_model=List[schemas.TareaRespuesta])
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


@app.post("/api/tareas", response_model=schemas.TareaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_tarea(datos: schemas.TareaCrear, db: Session = Depends(database.obtener_db)):
    """
    Registra una nueva tarea en la base de datos.
    Si se indica lead_id, verifica que el lead exista antes de asociarlo.
    """
    from datetime import date as date_type

    if datos.lead_id:
        lead = db.query(models.Lead).filter(models.Lead.id == datos.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")

    # Convertir fecha_limite de string ISO a objeto date si se proporcionó
    fecha_limite_obj = None
    if datos.fecha_limite:
        try:
            fecha_limite_obj = date_type.fromisoformat(datos.fecha_limite)
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


@app.put("/api/tareas/{tarea_id}", response_model=schemas.TareaRespuesta)
def actualizar_tarea(tarea_id: int, datos: schemas.TareaActualizar, db: Session = Depends(database.obtener_db)):
    """
    Actualiza los campos de una tarea existente.
    Solo modifica los campos enviados en el body.
    Devuelve 404 si la tarea no existe.
    """
    from datetime import date as date_type

    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    campos = datos.model_dump(exclude_unset=True)

    # Tratar fecha_limite por separado para convertirla a objeto date
    if "fecha_limite" in campos:
        valor_fecha = campos.pop("fecha_limite")
        if valor_fecha:
            try:
                tarea.fecha_limite = date_type.fromisoformat(valor_fecha)
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


@app.delete("/api/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
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

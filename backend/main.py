from fastapi import FastAPI, Depends, status
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


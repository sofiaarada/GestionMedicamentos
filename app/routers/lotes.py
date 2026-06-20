from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/lotes",
    tags=["Lotes e Inventario"]
)

@router.post("/", response_model=schemas.LoteResponse, status_code=status.HTTP_201_CREATED)
def registrar_lote(lote: schemas.LoteCreate, db: Session= Depends(get_db)):
    medicamento_db = db.query(models.Medicamento).filter(
        models.Medicamento.id_medicamento == lote.id_medicamento,
        models.Medicamento.activo == True
    ).first()
    
    if not medicamento_db: 
        raise HTTPException(status_code=404, detail="El medicamento no existe o esta inactivo.")
    if lote.cantidad_inicial <= 0:
        raise HTTPException(status_code=400, detail="La cantidad incial debe ser mayor a 0.")
    
    if lote.cantidad_actual > lote.cantidad_inicial:
        raise HTTPException(status_code=400, detail="La cantidad actual no puede ser mayor a la incial.")
    
    if lote.fecha_vencimiento <= lote.fecha_entrada:
        raise HTTPException(status_code=400, detail="La fecha  de vencimiento debe ser posterior a la fecha de entrada.")
    
    nuevo_lote = models.Lote(**lote.model_dump())
    db.add(nuevo_lote)
    db.commit()
    db.refresh(nuevo_lote)
    
    return nuevo_lote

@router.get("/", response_model=List[schemas.LoteResponse])
def obtener_lotes(db: Session = Depends(get_db)):
    lotes = db.query(models.Lote).all()
    return lotes
    
    

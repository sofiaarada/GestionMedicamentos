from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/movimientos",
    tags=["Transacciones (Historial para ML)"]
)

@router.post("/", response_model=schemas.MovimientoResponse, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):

    usuario_db = db.query(models.Usuario).filter(models.Usuario.id_usuario == movimiento.id_usuario).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    lote_db = db.query(models.Lote).filter(models.Lote.id_lote == movimiento.id_lote).first()
    if not lote_db:
        raise HTTPException(status_code=404, detail="Lote no encontrado.")
        
    if movimiento.tipo_movimiento == 'SALIDA':
        if lote_db.cantidad_actual < movimiento.cantidad_movimiento:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente. Solo hay {lote_db.cantidad_actual} unidades disponibles.")
        lote_db.cantidad_actual -= movimiento.cantidad_movimiento
        
    elif movimiento.tipo_movimiento == 'ENTRADA':
        lote_db.cantidad_actual += movimiento.cantidad_movimiento
        
    else:
        raise HTTPException(status_code=400, detail="El tipo de movimiento debe ser exactamente 'ENTRADA' o 'SALIDA'.")
        
    nuevo_movimiento = models.Movimiento(**movimiento.model_dump())
    db.add(nuevo_movimiento)
    db.add(lote_db)
    db.commit()
    db.refresh(nuevo_movimiento)
    
    return nuevo_movimiento

@router.get("/", response_model=List[schemas.MovimientoResponse])
def obtener_movimientos(db: Session = Depends(get_db)):
    return db.query(models.Movimiento).all()
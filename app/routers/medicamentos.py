from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/medicamentos",
    tags=["Medicamentos"]
)

@router.post("/", response_model=schemas.MedicamentoResponse, status_code=status.HTTP_201_CREATED)
def crear_medicamento(medicamento: schemas.MedicamentoCreate, db: Session = Depends(get_db)):
    categoria_db = db.query(models.Categoria).filter(models.Categoria.id_categoria == medicamento.id_categoria).first()
    if not categoria_db:
        raise HTTPException(status_code=404, detail=f"La categoria con ID {medicamento.id_categoria} no existe. ")
    nuevo_medicamento = models.Medicamento(**medicamento.model_dump())
    
    db.add(nuevo_medicamento)
    db.commit()
    db.refresh(nuevo_medicamento)
    
    return nuevo_medicamento

@router.get("/", response_model=List[schemas.MedicamentoResponse])
def obtener_medicamentos(db: Session = Depends(get_db)):
    medicamentos = db.query(models.Medicamento).filter(models.Medicamento.activo == True).all()
    return medicamentos

@router.delete("/{id_medicamento}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medicamento(id_medicamento: int, db: Session = Depends(get_db)):
    medicamento_db = db.query(models.Medicamento).filter(models.Medicamento.id_medicamento == id_medicamento).first()
    
    if not medicamento_db:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado.")
    
    medicamento_db.activo = False
    db.commit()
    
    return
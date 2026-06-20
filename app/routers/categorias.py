from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/categorias",
    tags=["categoria"]
)

@router.post("/", response_model=schemas.CategoriaResponse, status_code=201)

def crear_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    categoria_existente = db.query(models.Categoria).filter(models.Categoria.nombre == categoria.nombre).first()
    
    if categoria_existente:
        raise HTTPException(status_code=400, detail="La categoria ya existe en la base de datos.")
    
    nueva_categoria = models.Categoria(nombre=categoria.nombre)
    
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    
    return nueva_categoria
    
@router.get("/", response_model=List[schemas.CategoriaResponse])
def obtener_categorias(db:Session = Depends(get_db)):
    categorias = db.query(models.Categoria).all()
    return categorias

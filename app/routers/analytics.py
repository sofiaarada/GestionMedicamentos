from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models import models

router = APIRouter(
    prefix="/analytics",
    tags=["Dashboard y Analíticas"]
)

@router.get("/summary")
def obtener_resumen_dashboard(db: Session = Depends(get_db)):

    total_medicamentos = db.query(models.Medicamento).filter(models.Medicamento.activo == True).count()
    
    lotes_criticos = db.query(models.Lote).join(models.Medicamento).filter(
        models.Medicamento.activo == True,
        models.Lote.cantidad_actual <= models.Medicamento.stock_minimo_alerta
    ).count()

    hoy = date.today()
    fecha_limite = hoy + timedelta(days=30)
    
    lotes_por_vencer = db.query(models.Lote).join(models.Medicamento).filter(
        models.Medicamento.activo == True,
        models.Lote.fecha_vencimiento >= hoy,
        models.Lote.fecha_vencimiento <= fecha_limite
    ).count()

    return {
        "total_medicamentos": total_medicamentos,
        "stock_critico": lotes_criticos,
        "proximos_vencer": lotes_por_vencer
    }
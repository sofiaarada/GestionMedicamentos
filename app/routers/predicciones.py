from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.ml.entrenamiento import predecir_demanda, pipeline_completo
import os

router = APIRouter(
    prefix="/predicciones",
    tags=["Predicciones ML"]
)

@router.get("/entrenar")
def entrenar_modelo(db: Session = Depends(get_db)):
    """
    Entrena el modelo de ML con los datos históricos de movimientos
    """
    try:
        success = pipeline_completo()
        
        if success:
            return {
                "status": "success",
                "mensaje": "Modelo entrenado exitosamente",
                "modelo": "Random Forest",
                "ubicacion": "app/ml/modelos/modelo_demanda.pkl"
            }
        else:
            return {
                "status": "warning",
                "mensaje": "No hay suficientes datos para entrenar el modelo"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al entrenar el modelo: {str(e)}"
        )

@router.post("/demanda/{medicamento_id}")
def predecir_demanda_medicamento(
    medicamento_id: int,
    consumo_promedio: float,
    cantidad_registros: int,
    db: Session = Depends(get_db)
):
    """
    Predice la demanda futura de un medicamento específico
    
    - **medicamento_id**: ID del medicamento
    - **consumo_promedio**: Consumo promedio histórico
    - **cantidad_registros**: Cantidad de registros históricos
    """
    try:
        # Verificar que el medicamento existe
        medicamento = db.query(models.Medicamento).filter(
            models.Medicamento.id_medicamento == medicamento_id
        ).first()
        
        if not medicamento:
            raise HTTPException(
                status_code=404,
                detail=f"Medicamento con ID {medicamento_id} no encontrado"
            )
        
        # Realizar predicción
        prediccion = predecir_demanda(medicamento_id, consumo_promedio, cantidad_registros)
        
        if prediccion is None:
            return {
                "medicamento_id": medicamento_id,
                "medicamento_nombre": medicamento.nombre,
                "prediccion": None,
                "mensaje": "Modelo no disponible. Debe entrenar primero con /predicciones/entrenar"
            }
        
        return {
            "medicamento_id": medicamento_id,
            "medicamento_nombre": medicamento.nombre,
            "prediccion_demanda": round(prediccion, 2),
            "unidad": medicamento.unidad_medida,
            "consumo_promedio_historico": consumo_promedio,
            "cantidad_registros_usados": cantidad_registros
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al predecir: {str(e)}"
        )

@router.get("/reporte")
def obtener_reporte_predicciones(db: Session = Depends(get_db)):
    """
    Genera un reporte de predicciones para todos los medicamentos activos
    """
    try:
        # Obtener modelo path
        from app.ml.entrenamiento import MODELS_DIR
        modelo_path = os.path.join(MODELS_DIR, "modelo_demanda.pkl")
        
        if not os.path.exists(modelo_path):
            return {
                "status": "warning",
                "mensaje": "Modelo no entrenado. Ejecute primero POST /predicciones/entrenar",
                "medicamentos": []
            }
        
        # Obtener medicamentos activos
        medicamentos = db.query(models.Medicamento).filter(
            models.Medicamento.activo == True
        ).all()
        
        if not medicamentos:
            return {
                "status": "info",
                "mensaje": "No hay medicamentos activos",
                "medicamentos": []
            }
        
        # Calcular estadísticas por medicamento
        predicciones = []
        for med in medicamentos:
            # Obtener consumo de los últimos 30 días
            from datetime import datetime, timedelta
            fecha_limite = datetime.now() - timedelta(days=30)
            
            consumos = db.query(models.Movimiento).join(
                models.Lote
            ).filter(
                models.Lote.id_medicamento == med.id_medicamento,
                models.Movimiento.tipo_movimiento == 'SALIDA',
                models.Movimiento.fecha_movimiento >= fecha_limite
            ).all()
            
            if len(consumos) > 0:
                consumo_total = sum(m.cantidad_movimiento for m in consumos)
                consumo_promedio = consumo_total / len(consumos)
                
                prediccion = predecir_demanda(
                    med.id_medicamento,
                    consumo_promedio,
                    len(consumos)
                )
                
                predicciones.append({
                    "medicamento_id": med.id_medicamento,
                    "medicamento": med.nombre,
                    "prediccion_proximos_30_dias": round(prediccion, 2) if prediccion else None,
                    "consumo_historico_30_dias": consumo_total,
                    "consumo_promedio": round(consumo_promedio, 2),
                    "registros": len(consumos)
                })
        
        return {
            "status": "success",
            "fecha_reporte": datetime.now().isoformat(),
            "total_medicamentos": len(predicciones),
            "medicamentos": predicciones
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte: {str(e)}"
        )

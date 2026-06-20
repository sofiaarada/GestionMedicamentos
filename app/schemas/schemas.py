from pydantic import BaseModel, ConfigDict 
from typing import Optional
from datetime import date, datetime

class CategoriaBase(BaseModel):
    nombre : str
    
class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id_categoria : int
    
    model_config = ConfigDict(from_attributes=True)
    
class MedicamentoBase(BaseModel):
    nombre: str
    id_categoria: int
    unidad_medida: str
    stock_minimo_alerta: int = 10
    activo: bool = True
    
class MedicamentoCreate(MedicamentoBase):
    pass

class MedicamentoResponse(MedicamentoBase):
    id_medicamento : int
    
    model_config = ConfigDict(from_attributes=True)
    
class LoteBase(BaseModel):
    id_medicamento : int
    cantidad_inicial : int
    cantidad_actual : int
    fecha_entrada : date
    fecha_vencimiento : date
    
class LoteCreate(LoteBase):
    pass

class LoteResponse(LoteBase):
    id_lote: int
    
    model_config = ConfigDict(from_attributes=True)
    
class MovimientoBase(BaseModel):
    id_lote : int
    id_usuario : int
    tipo_movimiento : str
    motivo_movimiento : str
    cantidad_movimiento : int
    
class MovimientoCreate(MovimientoBase):
    pass

class MovimientoResponse(MovimientoBase):
    id_movimiento : int
    fecha_movimiento : datetime
    
    model_config = ConfigDict(from_attributes=True)
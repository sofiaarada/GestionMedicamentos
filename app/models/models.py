from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Enum as SQLEnum

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    
    medicamentos = relationship("Medicamento", back_populates="categoria")
    
class Medicamento(Base):
    __tablename__ = "medicamentos"

    id_medicamento = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    unidad_medida = Column(String(50), nullable=False)
    stock_minimo_alerta = Column(Integer, nullable=False, default=10)
    activo = Column(Boolean, nullable=False, default=True)

    categoria = relationship("Categoria", back_populates="medicamentos")
    lotes = relationship("Lote", back_populates="medicamento")

class Lote(Base):
    __tablename__ = "lotes"

    id_lote = Column(Integer, primary_key=True, autoincrement=True)
    id_medicamento = Column(Integer, ForeignKey("medicamentos.id_medicamento"), nullable=False)
    cantidad_inicial = Column(Integer, nullable=False)
    cantidad_actual = Column(Integer, nullable=False)
    fecha_entrada = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)

    medicamento = relationship("Medicamento", back_populates="lotes")
    movimientos = relationship("Movimiento", back_populates="lote")

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    correo = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    movimientos = relationship("Movimiento", back_populates="usuario")

class Movimiento(Base):
    __tablename__ = "movimientos"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_lote = Column(Integer, ForeignKey("lotes.id_lote"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo_movimiento = Column(SQLEnum('ENTRADA', 'SALIDA'), nullable=False)
    motivo_movimiento = Column(String(100), nullable=False)
    cantidad_movimiento = Column(Integer, nullable=False)
    fecha_movimiento = Column(DateTime, server_default=func.now())

    lote = relationship("Lote", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")
    
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class Producto(Base):
    __tablename__ = "productos"

    id                  = Column(Integer, primary_key=True, index=True)
    nombre              = Column(String(150), nullable=False)
    descripcion         = Column(String(255))
    precio_compra       = Column(Float, nullable=False)
    precio_venta        = Column(Float, nullable=False)
    stock_actual        = Column(Integer, nullable=False, default=0)
    stock_minimo        = Column(Integer, nullable=False, default=5)
    categoria_id        = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())



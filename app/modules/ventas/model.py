from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class Venta(Base):
    __tablename__ = "ventas"

    id                  = Column(Integer, primary_key=True, index=True)
    usuario_id          = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha               = Column(DateTime, server_default=func.now())
    total_calculado     = Column(Float, default=0.0)
    ganancia_calculada  = Column(Float, default=0.0)
    estado              = Column(String(20), default="pagado")  # pagado o pendiente

    usuario  = relationship("Usuario")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")

class DetalleVenta(Base):
    __tablename__ = "detalles_venta"

    id              = Column(Integer, primary_key=True, index=True)
    venta_id        = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id     = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad        = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)   # precio de venta 
    subtotal        = Column(Float, nullable=False)    # precio(de cada uno ps) × cantidad
    ganancia_linea  = Column(Float, nullable=False)   # (precio de venta - precio de compra) por la cantidad

    venta    = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")


class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id          = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo        = Column(String(10), nullable=False)  # entrada o salida
    cantidad    = Column(Integer, nullable=False)
    motivo      = Column(String(255))
    fecha       = Column(DateTime, server_default=func.now())

    producto = relationship("Producto", back_populates="movimientos_stock")

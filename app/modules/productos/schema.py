from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime


class ProductoCreate(BaseModel):
    nombre:        str
    descripcion:   Optional[str] = None
    precio_compra: float
    precio_venta:  float
    stock_actual:  int
    stock_minimo:  int = 5
    categoria_id:  int

    @model_validator(mode="after")
    def precio_venta_mayor(self):
        if self.precio_venta <= self.precio_compra:
            raise ValueError("El precio de venta debe ser mayor al precio de compra.")
        if self.stock_actual < 0 or self.stock_minimo < 0:
            raise ValueError("El stock no puede ser negativo.")
        return self


class ProductoUpdate(BaseModel):
    nombre:        Optional[str]   = None
    descripcion:   Optional[str]   = None
    precio_compra: Optional[float] = None
    precio_venta:  Optional[float] = None
    stock_minimo:  Optional[int]   = None
    categoria_id:  Optional[int]   = None


class ProductoOut(BaseModel):
    id:                  int
    nombre:              str
    descripcion:         Optional[str]      = None
    precio_compra:       float
    precio_venta:        float
    stock_actual:        int
    stock_minimo:        int
    categoria_id:        int
    fecha_actualizacion: Optional[datetime] = None
    en_stock_critico:    bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_flag(cls, producto):
        obj = cls.model_validate(producto)
        obj.en_stock_critico = producto.stock_actual <= producto.stock_minimo
        return obj

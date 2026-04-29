from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemVenta(BaseModel):
    producto_id: int
    cantidad:    int


class VentaCreate(BaseModel):
    items:  list[ItemVenta]
    estado: str = "pagado"


class DetalleVentaOut(BaseModel):
    id:              int
    producto_id:     int
    cantidad:        int
    precio_unitario: float
    subtotal:        float
    ganancia_linea:  float

    model_config = {"from_attributes": True}


class VentaOut(BaseModel):
    id:                 int
    usuario_id:         int
    fecha:              Optional[datetime] = None
    total_calculado:    float
    ganancia_calculada: float
    estado:             str
    detalles:           list[DetalleVentaOut] = []
    stock_critico:      list[str] = []  

    model_config = {"from_attributes": True}


class ResumenVentas(BaseModel):
    periodo:            str
    total_ventas:       int
    ingresos_totales:   float
    ganancias_totales:  float

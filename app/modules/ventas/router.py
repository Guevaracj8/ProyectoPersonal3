from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.database.db import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.modules.usuarios.model import Usuario
from app.modules.productos.model import Producto
from .model import Venta, DetalleVenta, MovimientoStock
from .schema import VentaCreate, VentaOut, ResumenVentas

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])


@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def registrar_venta(
    data: VentaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto.")

    total       = 0.0
    ganancia    = 0.0
    detalles    = []
    criticos    = []

    for item in data.items:
        producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto ID {item.producto_id} no encontrado.")
        if item.cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero.")
        if producto.stock_actual < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock_actual}."
            )

    for item in data.items:
        producto        = db.query(Producto).filter(Producto.id == item.producto_id).first()
        subtotal        = round(producto.precio_venta * item.cantidad, 2)
        ganancia_linea  = round((producto.precio_venta - producto.precio_compra) * item.cantidad, 2)

        total    += subtotal
        ganancia += ganancia_linea

        detalle = DetalleVenta(
            producto_id     = item.producto_id,
            cantidad        = item.cantidad,
            precio_unitario = producto.precio_venta,
            subtotal        = subtotal,
            ganancia_linea  = ganancia_linea,
        )
        detalles.append(detalle)

        producto.stock_actual -= item.cantidad
        movimiento = MovimientoStock(
            producto_id = item.producto_id,
            usuario_id  = usuario.id,
            tipo        = "salida",
            cantidad    = item.cantidad,
            motivo      = f"Venta registrada",
        )
        db.add(movimiento)

        if producto.stock_actual <= producto.stock_minimo:
            criticos.append(producto.nombre)

    venta = Venta(
        usuario_id         = usuario.id,
        total_calculado    = round(total, 2),
        ganancia_calculada = round(ganancia, 2),
        estado             = data.estado,
    )
    db.add(venta)
    db.flush()  

    for detalle in detalles:
        detalle.venta_id = venta.id
        db.add(detalle)

    db.commit()
    db.refresh(venta)

    result             = VentaOut.model_validate(venta)
    result.stock_critico = criticos
    return result


@router.get("/", response_model=list[VentaOut])
def listar_ventas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin:    Optional[datetime] = Query(None),
    vendedor_id:  Optional[int]      = Query(None),
):
    q = db.query(Venta)

    if usuario.rol == "vendedor":
        q = q.filter(Venta.usuario_id == usuario.id)
    elif vendedor_id:
        q = q.filter(Venta.usuario_id == vendedor_id)

    if fecha_inicio:
        q = q.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Venta.fecha <= fecha_fin)

    return q.order_by(Venta.fecha.desc()).all()


@router.get("/resumen", response_model=ResumenVentas)
def resumen_ventas(
    periodo: str = Query("semanal", enum=["diario", "semanal", "mensual"]),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    hoy = datetime.utcnow()
    if periodo == "diario":
        desde = hoy - timedelta(days=1)
    elif periodo == "semanal":
        desde = hoy - timedelta(weeks=1)
    else:
        desde = hoy - timedelta(days=30)

    ventas = db.query(Venta).filter(Venta.fecha >= desde).all()
    return ResumenVentas(
        periodo           = periodo,
        total_ventas      = len(ventas),
        ingresos_totales  = round(sum(v.total_calculado for v in ventas), 2),
        ganancias_totales = round(sum(v.ganancia_calculada for v in ventas), 2),
    )


@router.get("/producto-mas-vendido")
def producto_mas_vendido(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin:    Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    q = db.query(
        DetalleVenta.producto_id,
        func.sum(DetalleVenta.cantidad).label("total_vendido")
    )
    if fecha_inicio:
        q = q.join(Venta).filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.join(Venta).filter(Venta.fecha <= fecha_fin)

    resultado = q.group_by(DetalleVenta.producto_id)\
                 .order_by(func.sum(DetalleVenta.cantidad).desc())\
                 .first()

    if not resultado:
        raise HTTPException(status_code=404, detail="No hay ventas en el período indicado.")

    producto = db.query(Producto).filter(Producto.id == resultado.producto_id).first()
    return {"producto": producto.nombre, "unidades_vendidas": resultado.total_vendido}


@router.get("/{venta_id}", response_model=VentaOut)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")
    if usuario.rol == "vendedor" and venta.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta venta.")
    return venta

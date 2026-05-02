from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import io

from app.database.db import get_db
from app.auth.dependencies import require_admin
from app.modules.usuarios.model import Usuario
from app.modules.ventas.model import Venta
from app.modules.productos.model import Producto
from app.utils.pdf_generator import generar_reporte_pdf, generar_recibo_pdf
from app.utils.excel_exporter import exportar_ventas_excel, exportar_inventario_excel

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def _rango_fechas(periodo: str):
    hoy = datetime.utcnow()
    if periodo == "diario":
        return hoy - timedelta(days=1), hoy
    elif periodo == "semanal":
        return hoy - timedelta(weeks=1), hoy
    else:
        return hoy - timedelta(days=30), hoy


@router.get("/pdf/ventas")
def reporte_pdf_ventas(
    periodo: str = Query("semanal", enum=["diario", "semanal", "mensual"]),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    desde, hasta = _rango_fechas(periodo)
    ventas = db.query(Venta).filter(Venta.fecha >= desde, Venta.fecha <= hasta).all()
    pdf_bytes = generar_reporte_pdf(ventas, periodo, desde, hasta)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=reporte_{periodo}.pdf"},
    )


@router.get("/pdf/recibo/{venta_id}")
def recibo_pdf(
    venta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    from fastapi import HTTPException
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")
    pdf_bytes = generar_recibo_pdf(venta)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=recibo_venta_{venta_id}.pdf"},
    )


@router.get("/excel/ventas")
def exportar_ventas(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin:    Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    q = db.query(Venta)
    if fecha_inicio:
        q = q.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Venta.fecha <= fecha_fin)
    ventas = q.all()
    excel_bytes = exportar_ventas_excel(ventas)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ventas.xlsx"},
    )


@router.get("/excel/inventario")
def exportar_inventario(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    productos = db.query(Producto).all()
    excel_bytes = exportar_inventario_excel(productos)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventario.xlsx"},
    )

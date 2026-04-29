from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.modules.usuarios.model import Usuario
from .model import Producto
from .schema import ProductoCreate, ProductoUpdate, ProductoOut

router = APIRouter(prefix="/api/productos", tags=["Productos"])


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    producto = Producto(**data.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return ProductoOut.from_orm_with_flag(producto)


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    productos = db.query(Producto).all()
    return [ProductoOut.from_orm_with_flag(p) for p in productos]


@router.get("/stock-critico", response_model=list[ProductoOut])
def stock_critico(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Devuelve productos cuyo stock_actual sea menor o igual al stock_minimo."""
    productos = db.query(Producto).filter(
        Producto.stock_actual <= Producto.stock_minimo
    ).all()
    return [ProductoOut.from_orm_with_flag(p) for p in productos]


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return ProductoOut.from_orm_with_flag(producto)


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return ProductoOut.from_orm_with_flag(producto)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    if producto.detalles_venta:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un producto con ventas registradas."
        )
    db.delete(producto)
    db.commit()

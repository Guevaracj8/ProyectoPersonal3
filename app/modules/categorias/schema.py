from pydantic import BaseModel
from typing import Optional


class CategoriaCreate(BaseModel):
    nombre:      str
    descripcion: Optional[str] = None


class CategoriaUpdate(BaseModel):
    nombre:      Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaOut(BaseModel):
    id:          int
    nombre:      str
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}

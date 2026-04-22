from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioCreate(BaseModel):
    nombre:     str
    apellido:   str
    email:      EmailStr
    password:   str
    rol:        str = "vendedor"  # admin | vendedor


class UsuarioUpdate(BaseModel):
    nombre:     Optional[str] = None
    apellido:   Optional[str] = None
    email:      Optional[EmailStr] = None
    activo:     Optional[bool] = None


class UsuarioOut(BaseModel):
    id:             int
    nombre:         str
    apellido:       str
    email:          str
    rol:            str
    activo:         bool
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    rol:          str

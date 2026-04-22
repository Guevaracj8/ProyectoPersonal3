from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database.db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id              = Column(Integer, primary_key=True, index=True)
    nombre          = Column(String(100), nullable=False)
    apellido        = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, nullable=False, index=True)
    password_hash   = Column(String(255), nullable=False)
    rol             = Column(String(20), nullable=False, default="vendedor")  # admin | vendedor
    activo          = Column(Boolean, default=True)
    fecha_creacion  = Column(DateTime, server_default=func.now())

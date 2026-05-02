from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255))

    productos = relationship("Producto", back_populates="categoria")

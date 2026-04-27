from fastapi import FastAPI
from app.database.db import Base, engine
from app.modules.usuarios.model import Usuario
from app.modules.categorias.model import Categoria        
from app.auth.router import router as auth_router
from app.modules.usuarios.router import router as usuarios_router
from app.modules.categorias.router import router as categorias_router 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.templates.views import router as views_router 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FerreStock API", version="1.0.0")

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(categorias_router) 

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(views_router)

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
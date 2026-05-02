from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router    = APIRouter(tags=["Vistas HTML"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/categorias", response_class=HTMLResponse)
def pagina_categorias(request: Request):
    return templates.TemplateResponse("categorias.html", {"request": request})


@router.get("/usuarios", response_class=HTMLResponse)
def pagina_usuarios(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})

@router.get("/productos", response_class=HTMLResponse)
def pagina_productos(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request})

@router.get("/ventas", response_class=HTMLResponse)
def pagina_ventas(request: Request):
    return templates.TemplateResponse("ventas.html", {"request": request}) 
    
@router.get("/reportes", response_class=HTMLResponse)
def pagina_ventas(request: Request):
    return templates.TemplateResponse("reportes.html", {"request": request})      
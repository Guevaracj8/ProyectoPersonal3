from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.auth.login_manager import autenticar_usuario
from app.modules.usuarios.schema import TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    return autenticar_usuario(form_data.username, form_data.password, db)


@router.post("/login/json", response_model=TokenResponse)
def login_json(data: LoginRequest, db: Session = Depends(get_db)):
    return autenticar_usuario(data.email, data.password, db)

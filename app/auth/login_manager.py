from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.modules.usuarios.model import Usuario
from app.auth.password import verify_password
from app.auth.jwt_handler import crear_token


def autenticar_usuario(email: str, password: str, db: Session) -> dict:

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacta al administrador.",
        )

    token = crear_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario.rol,
    }

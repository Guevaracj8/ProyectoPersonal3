from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

SECRET_KEY  = "clave_secreta_muy_larga_y_super_segura_para_el_jwt_de_la_app"
ALGORITHM   = "HS256"
EXPIRE_MINS = 60 * 8


def crear_token(data: dict) -> str:
    payload = data.copy()
    expira  = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINS)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

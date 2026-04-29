# DEPENDENCIAS DE AUTENTICACION
# Este archivo contiene las funciones inyectables de FastAPI (Dependencies)
# que protegen las rutas. Extraen y validan el token JWT que el usuario
# envia al header de la peticion HTTP.

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenData
from config.settings import ALGORITHM, SECRET_KEY


# Define de donde sacar el token (en este caso de la URL /auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _credentials_exception() -> HTTPException:
    """Helper para generar un error 401 unificado cuando falla la autenticacion."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    DEPENDENCIA PRINCIPAL: Extrae, valida el token JWT y retorna el usuario autenticado.
    
    1. Decodifica el token usando la SECRET_KEY.
    2. Extrae el nombre de usuario (claim 'sub').
    3. Busca al usuario en la base de datos.
    4. Si todo es correcto, inyecta el objeto 'user' en la ruta.
    """
    credentials_exception = _credentials_exception()

    try:
        # Intentamos decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extraemos la identidad del usuario
        token_data = TokenData(username=payload.get("sub"))
    except JWTError as exc:
        # Si el token es invalido, expiro o fue manipulado
        raise credentials_exception from exc

    if token_data.username is None:
        raise credentials_exception

    # Verificamos que el usuario del token realmente exista en nuestra DB
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user

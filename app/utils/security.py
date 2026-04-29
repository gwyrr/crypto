# UTILIDADES DE SEGURIDAD (Criptografia)
# Este modulo se encarga de manejar el cifrado de contrasenas (Hash) usando bcrypt
# y de generar los JSON Web Tokens (JWT) para mantener las sesiones de los usuarios.

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt de la contrasena proporcionada."""
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contrasena contra su hash bcrypt."""
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Genera un token JWT (JSON Web Token) incluyendo la fecha de expiracion y lo firma 
    utilizando el algoritmo seguro preconfigurado.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

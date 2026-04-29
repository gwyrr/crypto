from pydantic import BaseModel


class Token(BaseModel):
    """
    ESQUEMA DE TOKEN JWT
    Define la estructura del objeto que se devuelve al usuario tras un login exitoso.
    """
    # El string del token generado
    access_token: str
    # El tipo de token (siempre sera 'bearer' para OAuth2)
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    ESQUEMA DE DATOS DEL TOKEN
    Representa la informacion que extraemos y validamos desde dentro de un JWT.
    """
    # El identificador del usuario (su username) contenido en el campo 'sub' del token
    username: str | None = None

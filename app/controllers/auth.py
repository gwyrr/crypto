# CONTROLADOR DE AUTENTICACION
# Se encarga exclusivamente del proceso de inicio de sesion (Login).
# Recibe las credenciales, las valida y responde con un token de acceso.

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token
from app.services.auth_service import auth_service


# Definicion del router para autenticacion
router = APIRouter(prefix="/auth", tags=["Autenticacion"])


@router.post("/login", response_model=Token)
def login_for_access_token(
    # OAuth2PasswordRequestForm extrae 'username' y 'password' desde el body (form-data)
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    ENDPOINT DE LOGIN
    Valida las credenciales del usuario y devuelve un JWT para las siguientes peticiones.
    """
    # 1. Autenticar usando el servicio
    user = auth_service.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )
    
    # 2. Generar el token JWT firmado
    access_token = auth_service.create_access_token_for_user(user)
    
    # 3. Responder con el token y el tipo (bearer)
    return {"access_token": access_token, "token_type": "bearer"}

# SERVICIO DE AUTENTICACION

# Este modulo centraliza la logica de validacion de credenciales y
# la generacion de sesiones seguras para los usuarios.

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import create_access_token, verify_password


class AuthService:
    """
    Clase encargada de gestionar la seguridad y autenticacion de los usuarios.
    """

    @staticmethod
    def _invalid_credentials_exception() -> HTTPException:
        """Helper para lanzar error 401 unificado cuando las credenciales fallan."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def authenticate_user(self, db: Session, username: str, password: str) -> User:
        """
        Valida que el usuario exista y que su contrasena coincida con el hash en la DB.
        """
        user = db.query(User).filter(User.username == username).first()
        
        # Verificamos existencia y luego comparamos el hash de la contrasena
        if user is None or not verify_password(password, user.hashed_password):
            raise self._invalid_credentials_exception()
            
        return user

    def create_access_token_for_user(self, user: User) -> str:
        """
        Genera un JWT (JSON Web Token) firmado para un usuario autenticado.
        """
        return create_access_token(data={"sub": user.username})


# Instancia unica del servicio para ser usada en los controladores
auth_service = AuthService()

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import create_access_token, verify_password


class AuthService:
    @staticmethod
    def _invalid_credentials_exception() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def authenticate_user(self, db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if user is None or not verify_password(password, user.hashed_password):
            raise self._invalid_credentials_exception()
        return user

    def create_access_token_for_user(self, user: User) -> str:
        return create_access_token(data={"sub": user.username})


auth_service = AuthService()

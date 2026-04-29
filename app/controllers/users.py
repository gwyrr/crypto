# CONTROLADOR DE USUARIOS
# Gestiona el ciclo de vida de los usuarios: registro, consulta de perfil y actualizacion.

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service


# Definicion del router para gestion de usuarios
router = APIRouter(prefix="/users", tags=["users"])


def _ensure_same_user(user_id: int, current_user: User) -> None:
    """Seguridad: Valida que el usuario solo pueda ver/editar su propio perfil."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este usuario",
        )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    REGISTRO DE USUARIO
    Crea una nueva cuenta en el sistema. No requiere autenticacion previa.
    """
    return user_service.create_user(db=db, user=user)


@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    MI PERFIL
    Retorna la informacion del usuario que esta actualmente autenticado.
    """
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    DETALLE DE USUARIO
    Consulta datos de un usuario especifico por ID. Solo permitido para el mismo usuario.
    """
    _ensure_same_user(user_id=user_id, current_user=current_user)
    return user_service.get_user(db=db, user_id=user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ACTUALIZAR PERFIL
    Permite al usuario cambiar su correo o nombre de usuario.
    """
    _ensure_same_user(user_id=user_id, current_user=current_user)
    return user_service.update_user(db=db, user_id=user_id, user=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ELIMINAR CUENTA
    Borra permanentemente la cuenta del usuario.
    """
    _ensure_same_user(user_id=user_id, current_user=current_user)
    user_service.delete_user(db=db, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

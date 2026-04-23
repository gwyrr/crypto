from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash


def list_users(db: Session):
    return db.query(User).order_by(User.id).all()


def get_user(db: Session, user_id: int):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def create_user(db: Session, user: UserCreate):
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="El correo ya esta registrado")

    try:
        hashed_password = get_password_hash(user.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El usuario o correo ya existe")

    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db=db, user_id=user_id)

    if user.username is not None and user.username != db_user.username:
        existing_username = (
            db.query(User)
            .filter(User.username == user.username, User.id != user_id)
            .first()
        )
        if existing_username:
            raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")
        db_user.username = user.username

    if user.email is not None and user.email != db_user.email:
        existing_email = (
            db.query(User)
            .filter(User.email == user.email, User.id != user_id)
            .first()
        )
        if existing_email:
            raise HTTPException(status_code=409, detail="El correo ya esta registrado")
        db_user.email = user.email

    if user.password is not None:
        try:
            db_user.hashed_password = get_password_hash(user.password)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El usuario o correo ya existe")

    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db=db, user_id=user_id)
    db.delete(db_user)
    db.commit()

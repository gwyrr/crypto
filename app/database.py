from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import SQLALCHEMY_DATABASE_URL


connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

#puente de conexion entre py y sqlite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

#genera las conexiones cada que se pidan
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#esta es la clase base
Base = declarative_base()

#obtiene la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

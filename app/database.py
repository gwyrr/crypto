from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import SQLALCHEMY_DATABASE_URL

# CONFIGURACION DEL MOTOR DE BASE DE DATOS (SQLAlchemy)

connect_args = {}
# SQLite requiere configuraciones especificas para no bloquear los hilos en FastAPI
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# 'engine' es el puente de conexion principal entre Python y la base de datos (SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

# 'SessionLocal' es la fabrica que genera nuevas sesiones (conexiones) cada vez que se piden
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 'Base' es la clase de la cual heredaran todos nuestros modelos (POO).
# Permite a SQLAlchemy mapear clases de Python a tablas SQL.
Base = declarative_base()


# INYECCION DE DEPENDENCIAS

def get_db():
    """
    Generador que crea una sesion de base de datos para cada peticion web (Request).
    Garantiza, mediante 'yield' y 'finally', que la conexion siempre se cierre al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

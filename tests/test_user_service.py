import unittest


from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.schemas.user import UserCreate
from app.services.user_service import create_user


class UserServiceTests(unittest.TestCase):
    """
    Suite de pruebas unitarias para el servicio de gestion de usuarios.
    Utiliza una base de datos SQLite en memoria para garantizar que las pruebas
    sean rapidas, aisladas y no afecten la base de datos real.
    """

    def setUp(self):
        """
        Configuracion inicial antes de cada prueba:
        1. Crea un motor de base de datos en memoria.
        2. Crea las tablas necesarias.
        3. Inicializa una sesion local.
        """
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(bind=self.engine)
        self.db = self.session_local()

    def tearDown(self):
        """
        Limpieza despues de cada prueba:
        1. Cierra la sesion de la base de datos.
        2. Destruye las tablas.
        3. Libera los recursos del motor.
        """
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_user_rejects_duplicate_email(self):
        """
        Prueba que el sistema no permita registrar dos usuarios con el mismo correo.
        Debe lanzar una excepcion HTTP 409 (Conflict).
        """
        # 1. Creamos dos usuarios con el mismo email pero diferente username
        first_user = UserCreate(
            username="joa",
            email="joa@gmail.com",
            password="admin123",
        )
        second_user = UserCreate(
            username="joa2",
            email="joa@gmail.com",
            password="admin123",
        )

        # 2. Guardamos el primer usuario exitosamente
        create_user(self.db, first_user)

        # 3. Intentamos guardar el segundo usuario y verificamos que falle
        with self.assertRaises(HTTPException) as context:
            create_user(self.db, second_user)

        # 4. Validamos que el error sea el esperado (409 Conflict)
        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "El correo ya esta registrado")


if __name__ == "__main__":
    unittest.main()

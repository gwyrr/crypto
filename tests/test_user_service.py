import unittest

import app.models
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.schemas.user import UserCreate
from app.services.user_service import create_user


class UserServiceTests(unittest.TestCase):
    def setUp(self):
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
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_user_rejects_duplicate_email(self):
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

        create_user(self.db, first_user)

        with self.assertRaises(HTTPException) as context:
            create_user(self.db, second_user)

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "El correo ya esta registrado")


if __name__ == "__main__":
    unittest.main()

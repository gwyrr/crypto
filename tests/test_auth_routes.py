import unittest

import app.models
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.dependencies.auth import get_current_user
from app.models.asset import Cryptocurrency
from app.models.transaction import Transaction
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.transaction_service import get_transaction
from app.utils.security import get_password_hash


class AuthSecurityTests(unittest.TestCase):
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

    def _create_user(self, username: str, email: str, password: str = "admin123") -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _create_crypto(self, name: str, symbol: str, api_id: str) -> Cryptocurrency:
        asset = Cryptocurrency(name=name, symbol=symbol, api_id=api_id)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def _create_transaction(self, user_id: int, asset_id: int) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            asset_id=asset_id,
            amount=1.0,
            buy_price=10000.0,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def test_authenticate_user_accepts_valid_credentials(self):
        user = self._create_user("joa", "joa@gmail.com")

        authenticated_user = auth_service.authenticate_user(
            db=self.db,
            username="joa",
            password="admin123",
        )

        self.assertEqual(authenticated_user.id, user.id)

    def test_get_current_user_returns_user_from_valid_token(self):
        user = self._create_user("joa", "joa@gmail.com")
        token = auth_service.create_access_token_for_user(user)

        current_user = get_current_user(token=token, db=self.db)

        self.assertEqual(current_user.id, user.id)
        self.assertEqual(current_user.username, "joa")

    def test_get_current_user_rejects_invalid_token(self):
        with self.assertRaises(HTTPException) as context:
            get_current_user(token="token-invalido", db=self.db)

        self.assertEqual(context.exception.status_code, 401)

    def test_get_transaction_rejects_access_from_other_user(self):
        owner = self._create_user("joa", "joa@gmail.com")
        intruder = self._create_user("ana", "ana@gmail.com")
        bitcoin = self._create_crypto("Bitcoin", "BTC", "bitcoin")
        transaction = self._create_transaction(user_id=owner.id, asset_id=bitcoin.id)

        with self.assertRaises(HTTPException) as context:
            get_transaction(db=self.db, transaction_id=transaction.id, user_id=intruder.id)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(
            context.exception.detail,
            "No tienes permiso para acceder a esta transaccion",
        )


if __name__ == "__main__":
    unittest.main()

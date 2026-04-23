import unittest
from unittest.mock import patch

import app.models
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.asset import Cryptocurrency
from app.models.transaction import Transaction
from app.models.user import User
from app.services.transaction_service import get_user_portfolio_report


class TransactionServicePortfolioTests(unittest.TestCase):
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

        self.user = User(
            username="joa",
            email="joa@gmail.com",
            hashed_password="hashed-password",
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def _create_crypto(self, name: str, symbol: str, api_id: str):
        asset = Cryptocurrency(name=name, symbol=symbol, api_id=api_id)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def _create_transaction(self, asset_id: int, amount: float, buy_price: float):
        transaction = Transaction(
            user_id=self.user.id,
            asset_id=asset_id,
            amount=amount,
            buy_price=buy_price,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def test_get_user_portfolio_report_returns_empty_summary_for_user_without_transactions(self):
        with patch("app.services.transaction_service.market_service.get_simple_prices") as mocked_prices:
            report = get_user_portfolio_report(self.db, self.user.id)

        mocked_prices.assert_not_called()
        self.assertEqual(report.user_id, self.user.id)
        self.assertEqual(report.total_investment, 0.0)
        self.assertEqual(report.current_total_value, 0.0)
        self.assertEqual(report.total_profit_loss, 0.0)
        self.assertEqual(report.assets, [])

    def test_get_user_portfolio_report_aggregates_transactions_and_market_prices(self):
        bitcoin = self._create_crypto("Bitcoin", "BTC", "bitcoin")
        ethereum = self._create_crypto("Ethereum", "ETH", "ethereum")

        self._create_transaction(asset_id=bitcoin.id, amount=1.0, buy_price=10000.0)
        self._create_transaction(asset_id=bitcoin.id, amount=0.5, buy_price=20000.0)
        self._create_transaction(asset_id=ethereum.id, amount=2.0, buy_price=1000.0)

        with patch(
            "app.services.transaction_service.market_service.get_simple_prices",
            return_value={
                "bitcoin": {"usd": 15000.0},
                "ethereum": {"usd": 1200.0},
            },
        ) as mocked_prices:
            report = get_user_portfolio_report(self.db, self.user.id)

        mocked_prices.assert_called_once_with(
            asset_ids=["bitcoin", "ethereum"],
            vs_currency="usd",
        )
        self.assertAlmostEqual(report.total_investment, 22000.0)
        self.assertAlmostEqual(report.current_total_value, 24900.0)
        self.assertAlmostEqual(report.total_profit_loss, 2900.0)

        assets_by_symbol = {asset.symbol: asset for asset in report.assets}
        self.assertEqual(set(assets_by_symbol), {"BTC", "ETH"})

        btc_report = assets_by_symbol["BTC"]
        self.assertAlmostEqual(btc_report.amount, 1.5)
        self.assertAlmostEqual(btc_report.purchase_value, 20000.0)
        self.assertAlmostEqual(btc_report.current_value, 22500.0)
        self.assertAlmostEqual(btc_report.profit_loss, 2500.0)
        self.assertAlmostEqual(btc_report.percentage_change, 12.5)

        eth_report = assets_by_symbol["ETH"]
        self.assertAlmostEqual(eth_report.amount, 2.0)
        self.assertAlmostEqual(eth_report.purchase_value, 2000.0)
        self.assertAlmostEqual(eth_report.current_value, 2400.0)
        self.assertAlmostEqual(eth_report.profit_loss, 400.0)
        self.assertAlmostEqual(eth_report.percentage_change, 20.0)

    def test_get_user_portfolio_report_rejects_unknown_user(self):
        with self.assertRaises(HTTPException) as context:
            get_user_portfolio_report(self.db, user_id=999)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Usuario no encontrado")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch


from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.asset import Cryptocurrency
from app.models.transaction import Transaction
from app.models.user import User
from app.services.transaction_service import get_user_portfolio_report


class TransactionServicePortfolioTests(unittest.TestCase):
    """
    Suite de pruebas unitarias para la generacion de reportes de portafolio.
    Verifica que los calculos de inversion, valor actual y ganancias sean correctos.
    """

    def setUp(self):
        """
        Configuracion inicial para cada prueba:
        1. Crea una base de datos SQLite en memoria.
        2. Crea las tablas necesarias.
        3. Crea un usuario de prueba para asociarle transacciones.
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

        # Creamos un usuario base para las pruebas
        self.user = User(
            username="joa",
            email="joa@gmail.com",
            hashed_password="hashed-password",
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        """
        Limpieza despues de cada prueba: cierra la sesion y destruye la base de datos temporal.
        """
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def _create_crypto(self, name: str, symbol: str, api_id: str):
        """Metodo auxiliar para crear criptomonedas en la DB de prueba."""
        asset = Cryptocurrency(name=name, symbol=symbol, api_id=api_id)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def _create_transaction(self, asset_id: int, amount: float, buy_price: float):
        """Metodo auxiliar para crear transacciones en la DB de prueba."""
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
        """
        Verifica que si un usuario no tiene transacciones, el reporte devuelva valores en cero.
        """
        with patch("app.services.transaction_service.market_service.get_simple_prices") as mocked_prices:
            report = get_user_portfolio_report(self.db, self.user.id)

        # No deberia llamar al servicio de mercado si no hay activos que consultar
        mocked_prices.assert_not_called()
        self.assertEqual(report.user_id, self.user.id)
        self.assertEqual(report.total_investment, 0.0)
        self.assertEqual(report.current_total_value, 0.0)
        self.assertEqual(report.total_profit_loss, 0.0)
        self.assertEqual(report.assets, [])

    def test_get_user_portfolio_report_aggregates_transactions_and_market_prices(self):
        """
        Prueba principal:
        1. Crea activos (BTC, ETH) y transacciones.
        2. Simula (mock) la respuesta de precios de la API externa.
        3. Verifica que los calculos de agregacion y rendimiento sean exactos.
        """
        bitcoin = self._create_crypto("Bitcoin", "BTC", "bitcoin")
        ethereum = self._create_crypto("Ethereum", "ETH", "ethereum")

        # Compras de prueba
        self._create_transaction(asset_id=bitcoin.id, amount=1.0, buy_price=10000.0)
        self._create_transaction(asset_id=bitcoin.id, amount=0.5, buy_price=20000.0) # Total 1.5 BTC, invertido 20k
        self._create_transaction(asset_id=ethereum.id, amount=2.0, buy_price=1000.0) # Total 2 ETH, invertido 2k

        # Simulamos que BTC subio a 15k y ETH a 1.2k
        with patch(
            "app.services.transaction_service.market_service.get_simple_prices",
            return_value={
                "bitcoin": {"usd": 15000.0},
                "ethereum": {"usd": 1200.0},
            },
        ) as mocked_prices:
            report = get_user_portfolio_report(self.db, self.user.id)

        # Verificamos la llamada al mock
        mocked_prices.assert_called_once_with(
            asset_ids=["bitcoin", "ethereum"],
            vs_currency="usd",
        )
        
        # Verificamos totales globales
        self.assertAlmostEqual(report.total_investment, 22000.0)
        self.assertAlmostEqual(report.current_total_value, 24900.0)
        self.assertAlmostEqual(report.total_profit_loss, 2900.0)

        # Verificamos el desglose por cada activo
        assets_by_symbol = {asset.symbol: asset for asset in report.assets}
        self.assertEqual(set(assets_by_symbol), {"BTC", "ETH"})

        # Validamos BTC (1.5 BTC * 15000 = 22500)
        btc_report = assets_by_symbol["BTC"]
        self.assertAlmostEqual(btc_report.amount, 1.5)
        self.assertAlmostEqual(btc_report.purchase_value, 20000.0)
        self.assertAlmostEqual(btc_report.current_value, 22500.0)
        self.assertAlmostEqual(btc_report.profit_loss, 2500.0)
        self.assertAlmostEqual(btc_report.percentage_change, 12.5)

        # Validamos ETH (2.0 ETH * 1200 = 2400)
        eth_report = assets_by_symbol["ETH"]
        self.assertAlmostEqual(eth_report.amount, 2.0)
        self.assertAlmostEqual(eth_report.purchase_value, 2000.0)
        self.assertAlmostEqual(eth_report.current_value, 2400.0)
        self.assertAlmostEqual(eth_report.profit_loss, 400.0)
        self.assertAlmostEqual(eth_report.percentage_change, 20.0)

    def test_get_user_portfolio_report_rejects_unknown_user(self):
        """
        Verifica que el sistema lance error 404 si se pide reporte de un usuario inexistente.
        """
        with self.assertRaises(HTTPException) as context:
            get_user_portfolio_report(self.db, user_id=999)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Usuario no encontrado")


if __name__ == "__main__":
    unittest.main()

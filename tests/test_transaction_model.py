import unittest

from app.models.transaction import Transaction


class TransactionModelTests(unittest.TestCase):
    """
    Pruebas unitarias para la logica interna de la clase Transaction.
    Verifica que los metodos de calculo del modelo funcionen correctamente.
    """

    def test_calculate_investment(self):
        """
        Verifica que el metodo calculate_investment multiplique correctamente
        la cantidad por el precio de compra.
        """
        # 1. Creamos una transaccion de prueba (2.5 unidades a 100.0 USD c/u)
        transaction = Transaction(amount=2.5, buy_price=100.0, type="buy")

        # 2. El total invertido deberia ser 250.0
        self.assertEqual(transaction.calculate_investment(), 250.0)


if __name__ == "__main__":
    unittest.main()

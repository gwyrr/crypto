import unittest

from app.models.transaction import Transaction


class TransactionModelTests(unittest.TestCase):
    def test_calculate_investment(self):
        transaction = Transaction(amount=2.5, buy_price=100.0)

        self.assertEqual(transaction.calculate_investment(), 250.0)


if __name__ == "__main__":
    unittest.main()

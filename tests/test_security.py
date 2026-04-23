import unittest

from app.utils.security import get_password_hash


class SecurityTests(unittest.TestCase):
    def test_password_hash_is_not_plain_text(self):
        password = "admin123"
        hashed_password = get_password_hash(password)

        self.assertNotEqual(password, hashed_password)
        self.assertTrue(hashed_password.startswith("$2"))


if __name__ == "__main__":
    unittest.main()

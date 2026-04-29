import unittest

from app.utils.security import get_password_hash


class SecurityTests(unittest.TestCase):
    """
    Pruebas basicas de seguridad para verificar el correcto funcionamiento
    de las utilidades de cifrado.
    """

    def test_password_hash_is_not_plain_text(self):
        """
        Verifica que la contrasena no se guarde en texto plano y que se
        utilice el algoritmo bcrypt (identificado por el prefijo $2).
        """
        password = "admin123"
        hashed_password = get_password_hash(password)

        # La contrasena hasheada no debe ser igual a la original
        self.assertNotEqual(password, hashed_password)
        # Bcrypt genera hashes que empiezan con $2
        self.assertTrue(hashed_password.startswith("$2"))


if __name__ == "__main__":
    unittest.main()

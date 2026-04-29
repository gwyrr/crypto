import os
from dotenv import load_dotenv

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()


# CONFIGURACION DE BASE DE DATOS

# URL de conexion para SQLAlchemy. Por defecto usa SQLite local.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./crypto_portfolio.db",
)


# CONFIGURACION DE API EXTERNA (CoinGecko)

# URL base para las consultas de precios de criptomonedas
COINGECKO_BASE_URL = os.getenv(
    "COINGECKO_BASE_URL",
    "https://api.coingecko.com/api/v3",
)
# Llave de API opcional (para planes pro de CoinGecko)
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
# Tiempo maximo de espera para las peticiones externas (en segundos)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))


# CONFIGURACION DE SEGURIDAD (JWT)

# Llave secreta para firmar los tokens JWT.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
# Algoritmo de cifrado para el token
ALGORITHM = "HS256"
# Tiempo de vida del token de acceso (1440 minutos = 24 horas por defecto)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

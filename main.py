# Este archivo es el corazon de la aplicacion FastAPI.
# Aqui se inicializa la base de datos, se configuran las rutas (controladores)
# y se levanta el servidor web junto con los archivos estaticos (frontend).
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import app.models
from app.controllers.assets import router as assets_router
from app.controllers.auth import router as auth_router
from app.controllers.market import router as market_router
from app.controllers.transactions import router as transactions_router
from app.controllers.users import router as users_router
from app.database import Base, SessionLocal, engine

# 1. INICIALIZACION DE LA BASE DE DATOS
# Crea las tablas en SQLite basandose en los modelos de SQLAlchemy si no existen.
Base.metadata.create_all(bind=engine)


def _seed_default_assets():
    """
    Puebla la base de datos con activos iniciales si esta vacia.
    Esto permite que el usuario tenga opciones predeterminadas al iniciar.
    """
    from app.models.asset import Cryptocurrency

    db = SessionLocal()
    try:
        if db.query(Cryptocurrency).count() == 0:
            defaults = [
                Cryptocurrency(name="Bitcoin", symbol="BTC", api_id="bitcoin"),
                Cryptocurrency(name="Ethereum", symbol="ETH", api_id="ethereum"),
                Cryptocurrency(name="Solana", symbol="SOL", api_id="solana"),
                Cryptocurrency(name="Cardano", symbol="ADA", api_id="cardano"),
                Cryptocurrency(name="Ripple", symbol="XRP", api_id="ripple"),
                Cryptocurrency(name="Dogecoin", symbol="DOGE", api_id="dogecoin"),
                Cryptocurrency(name="Polkadot", symbol="DOT", api_id="polkadot"),
                Cryptocurrency(name="Chainlink", symbol="LINK", api_id="chainlink"),
            ]
            db.add_all(defaults)
            db.commit()
    finally:
        db.close()

# Ejecutamos la siembra de datos al levantar el servidor
_seed_default_assets()

# 2. CONFIGURACION DE FASTAPI

app = FastAPI(title="Crypto Portfolio API", version="0.1.0")

# 3. REGISTRO DE RUTAS (ENDPOINTS)

# Aqui conectamos todos los controladores que manejan las peticiones HTTP
app.include_router(auth_router)         # Rutas de autenticacion (Login)
app.include_router(users_router)        # Rutas de gestion de usuarios (Registro)
app.include_router(assets_router)       # Rutas de activos disponibles
app.include_router(transactions_router) # Rutas de transacciones de portafolio
app.include_router(market_router)       # Rutas para consultar precios externos (CoinGecko)

# 4. CONFIGURACION DEL FRONTEND

# Montamos la carpeta "app/static" para servir los archivos HTML, CSS y JS
app.mount("/app", StaticFiles(directory="app/static", html=True), name="static")

@app.get("/")
def home():
    """
    Redirige la raiz del sitio a la interfaz grafica (frontend web).
    """
    return RedirectResponse(url="/app/")


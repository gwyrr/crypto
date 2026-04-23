from app.controllers.assets import router as assets_router
from app.controllers.auth import router as auth_router
from app.controllers.market import router as market_router
from app.controllers.transactions import router as transactions_router
from app.controllers.users import router as users_router

__all__ = [
    "assets_router",
    "auth_router",
    "market_router",
    "transactions_router",
    "users_router",
]

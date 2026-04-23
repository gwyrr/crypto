from fastapi import FastAPI

import app.models
from app.controllers.assets import router as assets_router
from app.controllers.auth import router as auth_router
from app.controllers.market import router as market_router
from app.controllers.transactions import router as transactions_router
from app.controllers.users import router as users_router
from app.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crypto Portfolio API", version="0.1.0")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(assets_router)
app.include_router(transactions_router)
app.include_router(market_router)


@app.get("/")
def home():
    return {"message": "Crypto Portfolio API activa"}

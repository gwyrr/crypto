from fastapi import APIRouter, HTTPException, Query

from app.schemas.market import MarketCoin
from app.services import market_service


router = APIRouter(prefix="/market", tags=["market"])


@router.get("/prices", response_model=dict[str, dict[str, float]])
def get_prices(
    ids: str = Query(..., description="Lista separada por comas de api_id"),
    vs_currency: str = Query(default="usd"),
):
    asset_ids = [item.strip().lower() for item in ids.split(",") if item.strip()]
    if not asset_ids:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un api_id")
    return market_service.get_simple_prices(asset_ids=asset_ids, vs_currency=vs_currency)


@router.get("/top", response_model=list[MarketCoin])
def get_top_cryptocurrencies(
    limit: int = Query(default=10, ge=1, le=50),
    vs_currency: str = Query(default="usd"),
):
    return market_service.get_top_cryptocurrencies(
        per_page=limit,
        vs_currency=vs_currency,
    )

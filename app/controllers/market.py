# CONTROLADOR DE MERCADO
# Este modulo gestiona las consultas de datos externos en tiempo real.
# Provee precios actuales y listas de tendencias de criptomonedas.

from fastapi import APIRouter, HTTPException, Query

from app.schemas.market import MarketCoin
from app.services import market_service


# Definicion del router para datos de mercado
router = APIRouter(prefix="/market", tags=["market"])


@router.get("/prices", response_model=dict[str, dict[str, float]])
def get_prices(
    # Recibe una lista de IDs (ej: 'bitcoin,ethereum')
    ids: str = Query(..., description="Lista separada por comas de api_id"),
    vs_currency: str = Query(default="usd"),
):
    """
    ENDPOINT DE PRECIOS SIMPLES
    Obtiene los precios actuales para una lista de criptomonedas (api_ids).
    """
    # Limpieza de los IDs recibidos en el string
    asset_ids = [item.strip().lower() for item in ids.split(",") if item.strip()]
    
    if not asset_ids:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un api_id")
        
    return market_service.get_simple_prices(asset_ids=asset_ids, vs_currency=vs_currency)


@router.get("/top", response_model=list[MarketCoin])
def get_top_cryptocurrencies(
    limit: int = Query(default=10, ge=1, le=50),
    vs_currency: str = Query(default="usd"),
):
    """
    ENDPOINT DE TENDENCIAS
    Consulta el top de criptomonedas mas populares segun capitalizacion de mercado.
    """
    return market_service.get_top_cryptocurrencies(
        per_page=limit,
        vs_currency=vs_currency,
    )

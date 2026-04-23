from pydantic import BaseModel


class MarketCoin(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float | None = None
    market_cap: float | None = None
    price_change_percentage_24h: float | None = None

from pydantic import BaseModel


class MarketCoin(BaseModel):
    """
    ESQUEMA DE DATOS DE MERCADO
    Representa la informacion en tiempo real que recibimos de APIs como CoinGecko.
    """
    # Identificador de la API (ej: 'bitcoin')
    id: str
    
    # Simbolo (ej: 'btc')
    symbol: str
    
    # Nombre (ej: 'Bitcoin')
    name: str
    
    # Precio actual en USD
    current_price: float | None = None
    
    # Capitalizacion de mercado
    market_cap: float | None = None
    
    # Cambio porcentual en las ultimas 24 horas
    price_change_percentage_24h: float | None = None

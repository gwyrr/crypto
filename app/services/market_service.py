# SERVICIO DE MERCADO
#
# Estrategia de APIs (sin costo):
#   - OHLC / Candlestick  -> Binance Public API  (1200 req/min, sin API key)
#   - Precios actuales     -> Binance Public API  (primario) con fallback a CoinGecko
#   - Top monedas          -> CoinGecko           (menos critico)
#
# Por que Binance?  La API publica de Binance no requiere autenticacion para
# datos de mercado y tiene limites mucho mas generosos que el plan gratuito de
# CoinGecko (~10 req/min).  Ademas, es la misma fuente que usa Binance en sus
# propias graficas.

from fastapi import HTTPException

from config.settings import COINGECKO_API_KEY, COINGECKO_BASE_URL, REQUEST_TIMEOUT

# URL base de la API publica de Binance (sin autenticacion)
BINANCE_BASE_URL = "https://api.binance.com/api/v3"

# Tabla de correspondencia: CoinGecko api_id  ->  simbolo de Binance (par USDT)
# Se extiende facilmente agregando mas monedas.
COINGECKO_TO_BINANCE: dict[str, str] = {
    "bitcoin":         "BTCUSDT",
    "ethereum":        "ETHUSDT",
    "solana":          "SOLUSDT",
    "cardano":         "ADAUSDT",
    "ripple":          "XRPUSDT",
    "dogecoin":        "DOGEUSDT",
    "polkadot":        "DOTUSDT",
    "chainlink":       "LINKUSDT",
    "binancecoin":     "BNBUSDT",
    "avalanche-2":     "AVAXUSDT",
    "matic-network":   "MATICUSDT",
    "uniswap":         "UNIUSDT",
    "litecoin":        "LTCUSDT",
    "stellar":         "XLMUSDT",
    "cosmos":          "ATOMUSDT",
    "tron":            "TRXUSDT",
    "near":            "NEARUSDT",
    "algorand":        "ALGOUSDT",
    "vechain":         "VETUSDT",
    "filecoin":        "FILUSDT",
    "aave":            "AAVEUSDT",
    "shiba-inu":       "SHIBUSDT",
    "internet-computer": "ICPUSDT",
    "hedera-hashgraph": "HBARUSDT",
    "aptos":           "APTUSDT",
    "arbitrum":        "ARBUSDT",
    "optimism":        "OPUSDT",
    "the-graph":       "GRTUSDT",
    "render-token":    "RENDERUSDT",
    "injective-protocol": "INJUSDT",
}


def _to_binance_symbol(coin_id: str) -> str:
    """
    Convierte un api_id de CoinGecko al simbolo de Binance.
    Si no esta en el mapa, intenta construirlo automaticamente (ej. 'bitcoin' -> 'BITCOINUSDT').
    """
    coin_id = coin_id.strip().lower()
    if coin_id in COINGECKO_TO_BINANCE:
        return COINGECKO_TO_BINANCE[coin_id]
    # Fallback: remover guiones y poner en mayusculas + USDT
    return coin_id.replace("-", "").upper() + "USDT"


def _get_requests_module():
    try:
        import requests
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="La dependencia 'requests' no esta instalada. Ejecuta: pip install -r requirements.txt",
        )
    return requests


# ---------------------------------------------------------------------------
# PRECIOS ACTUALES (Binance primario, CoinGecko como fallback)
# ---------------------------------------------------------------------------

def get_simple_prices(asset_ids: list[str], vs_currency: str = "usd") -> dict:
    """
    Obtiene el precio actual de una lista de criptomonedas.
    Usa Binance como fuente primaria y CoinGecko como respaldo.
    Retorna el mismo formato que antes: { "bitcoin": { "usd": 60000.0 }, ... }
    """
    try:
        return _get_prices_from_binance(asset_ids, vs_currency)
    except Exception:
        # Si Binance falla, intentamos con CoinGecko
        return _get_prices_from_coingecko(asset_ids, vs_currency)


def _get_prices_from_binance(asset_ids: list[str], vs_currency: str) -> dict:
    """
    Obtiene precios desde Binance usando el endpoint ticker/price.
    Sin API key, sin limites estrictos.
    """
    requests = _get_requests_module()
    result: dict[str, dict] = {}

    for coin_id in asset_ids:
        symbol = _to_binance_symbol(coin_id)
        try:
            response = requests.get(
                f"{BINANCE_BASE_URL}/ticker/price",
                params={"symbol": symbol},
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                data = response.json()
                price = float(data.get("price", 0))
                result[coin_id] = {vs_currency: price}
            else:
                result[coin_id] = {vs_currency: 0.0}
        except Exception:
            result[coin_id] = {vs_currency: 0.0}

    return result


def _get_prices_from_coingecko(asset_ids: list[str], vs_currency: str) -> dict:
    """
    Fallback: obtiene precios desde CoinGecko.
    """
    requests = _get_requests_module()
    headers = {"accept": "application/json"}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY

    try:
        response = requests.get(
            f"{COINGECKO_BASE_URL}/simple/price",
            params={
                "ids": ",".join(asset_ids),
                "vs_currencies": vs_currency.lower(),
            },
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    # Si ambas APIs fallan, retornamos ceros para no romper el portafolio
    return {coin_id: {vs_currency: 0.0} for coin_id in asset_ids}


# ---------------------------------------------------------------------------
# TOP MONEDAS (CoinGecko - menos critico, se llama poco)
# ---------------------------------------------------------------------------

def get_top_cryptocurrencies(per_page: int = 10, vs_currency: str = "usd"):
    """
    Consulta las principales criptomonedas ordenadas por capitalizacion de mercado.
    Sigue usando CoinGecko porque Binance no provee este dato directamente.
    """
    requests = _get_requests_module()
    headers = {"accept": "application/json"}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY

    try:
        response = requests.get(
            f"{COINGECKO_BASE_URL}/coins/markets",
            params={
                "vs_currency": vs_currency.lower(),
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": 1,
                "sparkline": "false",
            },
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    return []


def get_price(api_id: str, vs_currency: str = "usd") -> float:
    """
    Obtiene el precio individual de un activo.
    """
    prices = get_simple_prices([api_id], vs_currency)
    if api_id in prices and vs_currency in prices[api_id]:
        return prices[api_id][vs_currency]
    return 0.0


# ---------------------------------------------------------------------------
# OHLC / CANDLESTICK (Binance - API publica, sin key, 1200 req/min)
# ---------------------------------------------------------------------------

# Mapa de dias solicitados -> intervalo de Binance
# Binance intervals: 1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
_DAYS_TO_INTERVAL: list[tuple[int, str, int]] = [
    # (dias_max, intervalo, limite_de_velas)
    (1,   "30m", 48),
    (7,   "4h",  42),
    (30,  "1d",  30),
    (90,  "1d",  90),
    (365, "1w",  53),
]


def get_ohlc_data(coin_id: str, vs_currency: str = "usd", days: int = 7) -> list:
    """
    Obtiene datos OHLC (Open, High, Low, Close) desde la API publica de Binance.

    Ventajas sobre CoinGecko:
      - Sin API key requerida
      - 1200 peticiones por minuto (vs ~10-30 de CoinGecko gratuito)
      - Datos en tiempo real del exchange real

    Retorna lista de velas compatible con TradingView Lightweight Charts:
      [{ "time": unix_seconds, "open": f, "high": f, "low": f, "close": f }, ...]
    """
    requests = _get_requests_module()

    # Elegir el intervalo adecuado segun los dias solicitados
    interval, limit = "4h", 42
    for max_days, iv, lim in _DAYS_TO_INTERVAL:
        if days <= max_days:
            interval, limit = iv, lim
            break
    else:
        interval, limit = "1w", 53

    symbol = _to_binance_symbol(coin_id)

    try:
        response = requests.get(
            f"{BINANCE_BASE_URL}/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
            },
            timeout=REQUEST_TIMEOUT,
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail=f"No se pudo conectar con Binance para obtener datos de {coin_id}",
        )

    if response.status_code == 400:
        # Binance devuelve 400 cuando el simbolo no existe
        raise HTTPException(
            status_code=404,
            detail=f"Simbolo '{symbol}' no encontrado en Binance. Verifica el api_id del activo.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Error en Binance API. Codigo: {response.status_code}",
        )

    raw = response.json()

    if not isinstance(raw, list) or len(raw) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos OHLC disponibles para '{coin_id}'",
        )

    # Formato Binance klines:
    # [open_time, open, high, low, close, volume, close_time, ...]
    candles = []
    for item in raw:
        candles.append({
            "time": item[0] // 1000,      # ms -> segundos Unix
            "open":  float(item[1]),
            "high":  float(item[2]),
            "low":   float(item[3]),
            "close": float(item[4]),
        })

    return candles

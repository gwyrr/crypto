from fastapi import HTTPException

from config.settings import COINGECKO_BASE_URL, REQUEST_TIMEOUT


def _get_requests_module():
    try:
        import requests
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="La dependencia requests no esta instalada. Ejecuta: pip install -r requirements.txt",
        )
    return requests


def _parse_json_response(response):
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Error consultando la API externa. Codigo: {response.status_code}",
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="La API externa devolvio una respuesta JSON invalida",
        )


def get_simple_prices(asset_ids: list[str], vs_currency: str = "usd"):
    requests = _get_requests_module()
    try:
        response = requests.get(
            f"{COINGECKO_BASE_URL}/simple/price",
            params={
                "ids": ",".join(asset_ids),
                "vs_currencies": vs_currency.lower(),
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="No fue posible conectarse con la API de mercado",
        )

    return _parse_json_response(response)


def get_top_cryptocurrencies(per_page: int = 10, vs_currency: str = "usd"):
    requests = _get_requests_module()
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
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="No fue posible conectarse con la API de mercado",
        )

    return _parse_json_response(response)

def get_price(api_id: str, vs_currency: str = "usd") -> float:
    prices = get_simple_prices([api_id], vs_currency)
    if api_id in prices and vs_currency in prices[api_id]:
        return prices[api_id][vs_currency]
    return 0.0

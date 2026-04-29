# SERVICIO DE MERCADO (Integracion con CoinGecko)
# Este archivo encapsula toda la comunicacion con la API externa de criptomonedas.
# Utiliza la libreria 'requests' para obtener precios reales y maneja caidas de red.

from fastapi import HTTPException

from config.settings import COINGECKO_API_KEY, COINGECKO_BASE_URL, REQUEST_TIMEOUT


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
    """
    Procesa de manera segura la respuesta de la API externa.
    Maneja codigos de error y posibles fallas de formato JSON.
    """
    if response.status_code != 200:
        error_detail = f"Error consultando la API externa. Codigo: {response.status_code}"
        try:
            # Intentar extraer mas informacion del error si la API responde con JSON
            err_json = response.json()
            if "error" in err_json:
                error_detail += f" - Detalle: {err_json['error']}"
        except Exception:
            pass
            
        raise HTTPException(
            status_code=502,
            detail=error_detail,
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="La API externa devolvio una respuesta JSON invalida",
        )


def get_simple_prices(asset_ids: list[str], vs_currency: str = "usd"):
    """
    Obtiene el precio de mercado actual para una lista de criptomonedas.
    Integra con CoinGecko utilizando la API Key provista en la configuracion.
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
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="No fue posible conectarse con la API de mercado",
        )

    return _parse_json_response(response)


def get_top_cryptocurrencies(per_page: int = 10, vs_currency: str = "usd"):
    """
    Consulta las principales criptomonedas ordenadas por capitalizacion de mercado.
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
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="No fue posible conectarse con la API de mercado",
        )

    return _parse_json_response(response)

def get_price(api_id: str, vs_currency: str = "usd") -> float:
    """
    Obtiene el precio individual de un activo segun su identificador de API.
    """
    prices = get_simple_prices([api_id], vs_currency)
    if api_id in prices and vs_currency in prices[api_id]:
        return prices[api_id][vs_currency]
    return 0.0

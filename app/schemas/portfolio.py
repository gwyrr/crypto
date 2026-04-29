from pydantic import BaseModel
from typing import List


class AssetPerformance(BaseModel):
    """
    ESQUEMA DE RENDIMIENTO POR ACTIVO
    Detalla la situacion financiera de una moneda especifica en la billetera del usuario.
    """
    # Simbolo de la moneda
    symbol: str
    # Cantidad total que posee el usuario
    amount: float
    # Valor total invertido (costo de adquisicion)
    purchase_value: float
    # Valor actual en mercado segun precios reales
    current_value: float
    # Ganancia o perdida neta en USD
    profit_loss: float
    # Cambio porcentual del rendimiento
    percentage_change: float


class PortfolioSummary(BaseModel):
    """
    ESQUEMA DE RESUMEN GLOBAL DEL PORTAFOLIO
    Consolida todas las inversiones de un usuario en un solo informe.
    """
    user_id: int
    # Suma de todo el dinero invertido actualmente
    total_investment: float
    # Valor de todo el portafolio si se vendiera hoy
    current_total_value: float
    # Balance total de ganancias/perdidas
    total_profit_loss: float
    # Listado detallado moneda por moneda
    assets: List[AssetPerformance]
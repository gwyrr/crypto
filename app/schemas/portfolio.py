from pydantic import BaseModel
from typing import List

class AssetPerformance(BaseModel):
    symbol: str
    amount: float
    purchase_value: float
    current_value: float
    profit_loss: float
    percentage_change: float

class PortfolioSummary(BaseModel):
    user_id: int
    total_investment: float
    current_total_value: float
    total_profit_loss: float
    assets: List[AssetPerformance]
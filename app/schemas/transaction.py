from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    asset_id: int
    amount: float = Field(gt=0)
    buy_price: float = Field(gt=0)


class TransactionUpdate(BaseModel):
    asset_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    buy_price: float | None = Field(default=None, gt=0)


class TransactionRead(BaseModel):
    id: int
    user_id: int
    asset_id: int
    amount: float
    buy_price: float
    date: datetime
    investment: float

    model_config = ConfigDict(from_attributes=True)

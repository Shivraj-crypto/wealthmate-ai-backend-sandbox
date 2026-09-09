# app/schemas.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StockResponse(BaseModel):
    id: int
    symbol: str
    name: str
    currency: str
    market_state: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StockPriceResponse(BaseModel):
    id: int
    stock_id: int
    price: float
    change_percent: float | None = None
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockWithPriceResponse(BaseModel):
    id: int
    symbol: str
    name: str
    currency: str
    market_state: str | None = None

    price: float
    change_percent: float | None = None
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
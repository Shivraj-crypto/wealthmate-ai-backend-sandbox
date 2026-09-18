from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StockResponse(BaseModel):
    id: int
    symbol: str
    name: str
    currency: str
    market_state: str | None = None
    current_price: float
    current_change_percent: float | None = None
    price_updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoricalPriceResponse(BaseModel):
    id: int
    stock_id: int
    price: float
    recorded_at: datetime
    interval: str

    model_config = ConfigDict(from_attributes=True)
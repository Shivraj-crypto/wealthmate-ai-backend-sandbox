from app.database import Base
from sqlalchemy import Integer, String, Column, ForeignKey, Float, DateTime, UniqueConstraint
from fastapi import HTTPException


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    market_state = Column(String)

    current_price = Column(Float, nullable=False)
    current_change_percent = Column(Float)
    price_updated_at = Column(DateTime, nullable=False)


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    interval = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "stock_id",
            "recorded_at",
            "interval",
            name="unique_stock_historical_price"
        ),
    )
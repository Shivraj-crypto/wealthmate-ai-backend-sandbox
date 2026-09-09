from app.database import Base
from sqlalchemy import Integer, String, Column, ForeignKey, Float, DateTime


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    market_state = Column(String)


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    change_percent = Column(Float)
    recorded_at = Column(DateTime, nullable=False, index=True)
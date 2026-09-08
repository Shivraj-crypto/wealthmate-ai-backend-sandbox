from app.database import Base
from sqlalchemy import Integer, Boolean, String, Column, ForeignKey, Float, DateTime


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True)
    name = Column(String)
    currency = Column(String)
    market_state = Column(String)


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    price = Column(Float)
    change_percent = Column(Float)
    recorded_at = Column(DateTime)



    







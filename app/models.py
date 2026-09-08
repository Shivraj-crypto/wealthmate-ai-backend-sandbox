from app.database import Base
from sqlalchemy import Integer, Boolean, String, Column, ForeignKey, Float, DateTime


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    change_percent = Column(Float)
    currency = Column(String)
    market_state = Column(String)
    updated_at = Column(DateTime)



    







from app.database import Base
from sqlalchemy import Integer, String, Column, ForeignKey, Float, DateTime, UniqueConstraint
from sqlalchemy import Text, JSON


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

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)

    # Massive article ID
    external_id = Column(String(128), unique=True, nullable=False, index=True)

    title = Column(Text, nullable=False)
    author = Column(String)
    description = Column(Text)

    article_url = Column(Text, nullable=False)
    image_url = Column(Text)

    publisher_name = Column(String)
    publisher_homepage_url = Column(Text)
    publisher_logo_url = Column(Text)
    publisher_favicon_url = Column(Text)

    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)

    tickers = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    insights = Column(JSON, default=list)


class NewsStock(Base):
    __tablename__ = "news_stocks"

    news_id = Column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE"),
        primary_key=True
    )

    stock_id = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE"),
        primary_key=True
    )
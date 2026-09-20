from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Stock, HistoricalPrice
from .yahoo_service import get_formatted_quotes, get_historical_prices


def ingest_stocks():
    # Get data from Yahoo Finance
    quotes = get_formatted_quotes(["AAPL", "GOOG", "MSFT"])

    if not quotes:
        print("No quotes received from Yahoo Finance")
        return

    db: Session = SessionLocal()

    try:
        for quote in quotes:

            # Check if stock already exists
            stock = (
                db.query(Stock)
                .filter(Stock.symbol == quote["symbol"])
                .first()
            )

            # If stock doesn't exist, create it
            if stock is None:
                stock = Stock(
                    symbol=quote["symbol"],
                    name=quote["shortName"],
                    currency=quote["currency"],
                    market_state=quote["marketState"],
                    current_price=quote["regularMarketPrice"],
                    current_change_percent=quote["regularMarketChangePercent"],
                    price_updated_at=datetime.now(timezone.utc),
                )

                db.add(stock)

            # If stock already exists, update current price
            else:
                stock.current_price = quote["regularMarketPrice"]
                stock.current_change_percent = quote["regularMarketChangePercent"]
                stock.price_updated_at = datetime.now(timezone.utc)

        db.commit()

        print(f"Successfully ingested {len(quotes)} stocks")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    ingest_stocks()
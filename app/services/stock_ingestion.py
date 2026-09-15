from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Stock, StockPrice
from .yahoo_service import get_formatted_quotes


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
                )

                db.add(stock)
                db.flush()

            # Create historical price record
            stock_price = StockPrice(
                stock_id=stock.id,
                price=quote["regularMarketPrice"],
                change_percent=quote["regularMarketChangePercent"],
                recorded_at=datetime.now(timezone.utc),
            )

            db.add(stock_price)

        db.commit()

        print(f"Successfully ingested {len(quotes)} stocks")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    ingest_stocks()
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Stock
from .yahoo_service import get_formatted_quotes


SYMBOLS = [
    "AAPL",
    "GOOG",
    "MSFT",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "AVGO",
    "GOOGL",
    "NFLX",
    'JNJ'
    # we'll expand this to 100+ next
]


def seed_stocks():
    db: Session = SessionLocal()

    try:
        for i in range(0, len(SYMBOLS), 25):

            batch = SYMBOLS[i:i + 25]

            quotes = get_formatted_quotes(batch)

            for quote in quotes:

                stock = (
                    db.query(Stock)
                    .filter(Stock.symbol == quote["symbol"])
                    .first()
                )

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

        db.commit()

        print(f"Successfully seeded {len(SYMBOLS)} stocks")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_stocks()
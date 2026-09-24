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
                db.flush()

            # If stock already exists, update current price
            else:
                stock.current_price = quote["regularMarketPrice"]
                stock.current_change_percent = quote["regularMarketChangePercent"]
                stock.price_updated_at = datetime.now(timezone.utc)

            # Get 1D historical price data
            historical_prices_1d = get_historical_prices(
                quote["symbol"],
                period="1d",
                interval="5m"
            )

            # Get 1W historical price data
            historical_prices_1w = get_historical_prices(
                quote["symbol"],
                period="5d",
                interval="1h"
            )

            # Get 1Y historical price data
            historical_prices_1y = get_historical_prices(
                quote["symbol"],
                period="1y",
                interval="1d"
            )

            historical_prices = (
                historical_prices_1d
                + historical_prices_1w
                + historical_prices_1y
            )

            for historical_price in historical_prices:

                existing = (
                    db.query(HistoricalPrice)
                    .filter(
                        HistoricalPrice.stock_id == stock.id,
                        HistoricalPrice.recorded_at == historical_price["recorded_at"],
                        HistoricalPrice.interval == historical_price["interval"]
                    )
                    .first()
                )

                if existing is None:
                    data = HistoricalPrice(
                        stock_id=stock.id,
                        price=historical_price["price"],
                        recorded_at=historical_price["recorded_at"],
                        interval=historical_price["interval"]
                    )

                    db.add(data)

        db.commit()

        print(f"Successfully ingested {len(quotes)} stocks")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    ingest_stocks()
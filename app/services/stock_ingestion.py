from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Stock, HistoricalPrice
from .yahoo_service import get_formatted_quotes, get_historical_prices
from .stock_symbols import get_stock_symbols


def ingest_current_prices():
    db: Session = SessionLocal()

    try:
        symbols = get_stock_symbols(db)

        if not symbols:
            print("No stocks found in database")
            return

        total_updated = 0

        for i in range(0, len(symbols), 25):

            batch = symbols[i:i + 25]

            quotes = get_formatted_quotes(batch)

            for quote in quotes:

                stock = (
                    db.query(Stock)
                    .filter(Stock.symbol == quote["symbol"])
                    .first()
                )

                if stock is None:
                    continue

                stock.current_price = quote["regularMarketPrice"]
                stock.current_change_percent = quote["regularMarketChangePercent"]
                stock.price_updated_at = datetime.now(timezone.utc)

                total_updated += 1

        db.commit()

        print(
            f"Successfully updated current prices for {total_updated} stocks"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def ingest_historical_prices():
    db: Session = SessionLocal()

    try:
        symbols = get_stock_symbols(db)

        if not symbols:
            print("No stocks found in database")
            return

        stocks = (
            db.query(Stock)
            .filter(Stock.symbol.in_(symbols))
            .all()
        )

        stock_map = {
            stock.symbol: stock
            for stock in stocks
        }

        total_updated = 0

        for i in range(0, len(symbols), 25):

            batch = symbols[i:i + 25]

            # 1D → 5m
            historical_prices_1d = get_historical_prices(
                batch,
                period="1d",
                interval="5m"
            )

            # 1W → 1h
            historical_prices_1w = get_historical_prices(
                batch,
                period="5d",
                interval="1h"
            )

            # 1M / 3M / 1Y → 1d
            historical_prices_1y = get_historical_prices(
                batch,
                period="1y",
                interval="1d"
            )

            # 5Y → 1wk
            historical_prices_5y = get_historical_prices(
                batch,
                period="5y",
                interval="1wk"
            )

            historical_prices = (
                historical_prices_1d
                + historical_prices_1w
                + historical_prices_1y
                + historical_prices_5y
            )

            for historical_price in historical_prices:

                stock = stock_map.get(
                    historical_price["symbol"]
                )

                if stock is None:
                    continue

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
                    total_updated += 1

        # Delete historical data older than 5 years
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365 * 5)

        db.query(HistoricalPrice).filter(
            HistoricalPrice.recorded_at < cutoff_date
        ).delete(
            synchronize_session=False
        )

        db.commit()

        print(
            f"Successfully updated historical prices: "
            f"{total_updated} new records"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    ingest_current_prices()
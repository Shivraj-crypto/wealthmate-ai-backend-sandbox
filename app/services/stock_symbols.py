from sqlalchemy.orm import Session

from ..models import Stock


def get_stock_symbols(db: Session):
    stocks = db.query(Stock.symbol).all()

    return [stock.symbol for stock in stocks]
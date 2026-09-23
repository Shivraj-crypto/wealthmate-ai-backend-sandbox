from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Path
from .database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .models import Stock, HistoricalPrice
from .schemas import StockResponse


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

class StockTicker(BaseModel):
    symbol : str = Field(min_length=1)


db_dependency_injection = Annotated[Session, Depends(get_db)]


@router.get("/stocks_price", status_code=status.HTTP_200_OK, response_model=StockResponse)

async def get_current_stock_price(db: db_dependency_injection, symbol: str):
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()

    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO DATA")

    return stock


@router.get("/stocks_history", status_code=status.HTTP_200_OK)
async def get_stock_history(
    db: db_dependency_injection,
    symbol: str,
    chart_range: str = "1d"
):
    stock = (
        db.query(Stock)
        .filter(Stock.symbol == symbol.upper())
        .first()
    )

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO DATA"
        )

    interval_map = {
        "1d": "5m",
        "1w": "1h",
        "1mo": "1d",
        "1y": "1d",
        "5y": "1wk"
    }

    interval = interval_map.get(chart_range)

    if interval is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid range"
        )

    history = (
        db.query(HistoricalPrice)
        .filter(
            HistoricalPrice.stock_id == stock.id,
            HistoricalPrice.interval == interval
        )
        .order_by(HistoricalPrice.recorded_at.asc())
        .all()
    )

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO HISTORICAL DATA"
        )

    return history

    

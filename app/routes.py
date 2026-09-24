from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Path
from .database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .models import Stock, HistoricalPrice
from .schemas import StockResponse
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


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



    

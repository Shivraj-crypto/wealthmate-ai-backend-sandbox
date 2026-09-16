from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Path
from .database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .models import Stock, StockPrice
from .schemas import StockPriceResponse


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


@router.get("/stocks_price", status_code=status.HTTP_200_OK, response_model=StockPriceResponse)

async def get_current_stock_price(db: db_dependency_injection, input: StockTicker):

    stock = db.query(Stock).filter(Stock.symbol == input.symbol.upper()).first()

    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO DATA")

    stock_data = db.query(StockPrice).filter(stock.id == StockPrice.stock_id).order_by(StockPrice.recorded_at.desc()).first()

    if stock_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO PRICE DATA"
        )

    return stock_data


    

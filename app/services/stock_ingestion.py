from app.services.yahoo_service import get_formatted_quotes
from ..database import SessionLocal
from ..models import Stock
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from ..schemas import *
from ..database import *

def get_db():
    db = SessionLocal()

    try:
        yield db
    
    finally:
        db.close()

#dependency-injection for databse

db_dependency_injection = Annotated[Session, Depends(get_db)]

quotes = get_formatted_quotes(["AAPL", "GOOL"])

def add_to_db(db :db_dependency_injection):
    data = Stock(
        symbol=quotes[0]["symbol"],
        name=quotes[0]["shortName"],
        currency=quotes[0]["currency"],
        market_state=quotes[0]["marketState"]
    )

    db.add(data)
    db.commit()
    db.refresh(data)


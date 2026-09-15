from ..database import engine, Base
from ..models import Stock, StockPrice

Base.metadata.create_all(bind=engine)

print("Tables created!")

#This .py file is used to create database tables from the SQLAlchemy models in PostgreSQL.
#It checks the models and creates tables like stocks and stock_prices if they don't already exist.
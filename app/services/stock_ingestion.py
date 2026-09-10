from app.services.yahoo_service import get_formatted_quotes

quotes = get_formatted_quotes(["AAPL", "MSFT", "GOOG"])

for quote in quotes:
    print(quote)
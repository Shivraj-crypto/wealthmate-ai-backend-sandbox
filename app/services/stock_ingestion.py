from app.services.yahoo_service import get_formatted_quotes

quotes = get_formatted_quotes(["AAPL", "MSFT", "GOOG"])

q = []
for quote in quotes:
    q.append(quote)

print(q)
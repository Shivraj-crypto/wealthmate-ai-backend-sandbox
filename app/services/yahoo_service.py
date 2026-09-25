import re

from fastapi import HTTPException
from yahooquery import Ticker
from ..models import Stock
from ..database import *
from datetime import datetime, timezone


def normalize_symbols(symbols):

    if isinstance(symbols, str):
        symbols = symbols.split(",")

    cleaned_symbols = []

    for symbol in symbols:
        symbol = symbol.strip()

        if symbol:
            symbol = symbol.upper()

            if symbol not in cleaned_symbols:
                cleaned_symbols.append(symbol)

    if not cleaned_symbols:
        raise HTTPException(400, "No symbols provided")

    if len(cleaned_symbols) > 25:
        raise HTTPException(400, "Too many symbols (max 25)")

    for symbol in cleaned_symbols:
        if not re.match(r"^[A-Z.-]+$", symbol):
            raise HTTPException(
                400,
                f"Invalid symbol format: {symbol}"
            )

    return cleaned_symbols


def format_quote(quote):

    return {
        "symbol": quote.get("symbol"),
        "shortName": quote.get("shortName"),
        "regularMarketPrice": quote.get("regularMarketPrice"),
        "regularMarketChangePercent": quote.get(
            "regularMarketChangePercent"
        ),
        "currency": quote.get("currency"),
        "marketState": quote.get("marketState"),
    }


def get_formatted_quotes(symbols):

    symbols = normalize_symbols(symbols)

    ticker = Ticker(symbols)
    data = ticker.price

    if not isinstance(data, dict):
        return []

    results = []

    for symbol in symbols:
        quote = data.get(symbol)

        if quote:
            quote["symbol"] = symbol
            results.append(format_quote(quote))

    return results

def get_historical_prices(symbol, period="1d", interval="5m"):

    ticker = Ticker(symbol)

    data = ticker.history(
        period=period,
        interval=interval
    )

    if data is None or data.empty:
        return []

    results = []

    for _, row in data.iterrows():

        recorded_at = row.name[1]

        if hasattr(recorded_at, "to_pydatetime"):
            recorded_at = recorded_at.to_pydatetime()

        if isinstance(recorded_at, datetime):
            if recorded_at.tzinfo is None:
                recorded_at = recorded_at.replace(
                    tzinfo=timezone.utc
                )
        else:
            recorded_at = datetime.combine(
                recorded_at,
                datetime.min.time(),
                tzinfo=timezone.utc
            )

        results.append({
            "symbol": symbol,
            "price": float(row["close"]),
            "recorded_at": recorded_at,
            "interval": interval
        })

    return results


if __name__ == "__main__":
    pass

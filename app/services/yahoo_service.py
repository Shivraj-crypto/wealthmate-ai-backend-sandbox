from datetime import datetime, timezone

import re

from fastapi import HTTPException
from yahooquery import Ticker


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


def get_historical_prices(symbols, period="1d", interval="5m"):

    symbols = normalize_symbols(symbols)

    ticker = Ticker(symbols)

    data = ticker.history(
        period=period,
        interval=interval
    )

    if data is None or data.empty:
        return []

    results = []

    for _, row in data.iterrows():

        symbol = row.name[0]
        recorded_at = row.name[1]

        if hasattr(recorded_at, "to_pydatetime"):
            recorded_at = recorded_at.to_pydatetime()

        if not isinstance(recorded_at, datetime):
            recorded_at = datetime.combine(
                recorded_at,
                datetime.min.time()
            )

        if recorded_at.tzinfo is None:
            recorded_at = recorded_at.replace(
                tzinfo=timezone.utc
            )

        results.append({
            "symbol": symbol,
            "price": float(row["close"]),
            "recorded_at": recorded_at,
            "interval": interval
        })

    return results
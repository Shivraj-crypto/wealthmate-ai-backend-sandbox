import os
import re
import time

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from yahooquery import Ticker


app = FastAPI()


# CORS

origins = os.getenv("CORS_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not origins else origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------
# In-memory cache
# ----------------------

cache = {}


def get_cache(key):
    if key not in cache:
        return None

    item = cache[key]

    if time.time() > item["expires_at"]:
        del cache[key]
        return None

    return item["value"]


def set_cache(key, value):
    cache[key] = {
        "value": value,
        "expires_at": time.time() + 5
    }


# ----------------------
# Utilities
# ----------------------

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


# ----------------------
# Routes
# ----------------------

@app.get("/stock/{symbol}")
def get_stock(symbol: str):

    symbol = normalize_symbols(symbol)[0]

    cache_key = f"q:{symbol}"

    cached = get_cache(cache_key)

    if cached:
        return cached

    result = get_formatted_quotes([symbol])

    if not result:
        raise HTTPException(404, "Symbol not found")

    set_cache(cache_key, result[0])

    return result[0]


@app.get("/stocks")
def get_stocks(symbols: str = Query(...)):

    symbols = normalize_symbols(symbols)

    cache_key = f"qs:{','.join(symbols)}"

    cached = get_cache(cache_key)

    if cached:
        return cached

    result = get_formatted_quotes(symbols)

    set_cache(cache_key, result)

    return result


@app.get("/health")
def health():

    return {"ok": True}


# Run:
# uvicorn main:app --port 3001
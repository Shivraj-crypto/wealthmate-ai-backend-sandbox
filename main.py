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
    allow_origins=(
        [x.strip() for x in origins.split(",") if x.strip()]
        if origins
        else ["*"]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# In-memory cache
# ----------------------

cache = {}  # key -> {"value": ..., "expires_at": ...}


def get_cache(key):
    item = cache.get(key)

    if not item:
        return None

    if time.time() > item["expires_at"]:
        del cache[key]
        return None

    return item["value"]


def set_cache(key, value, ttl=5):
    cache[key] = {
        "value": value, 
        "expires_at": time.time() + ttl,
    }


# ----------------------
# Utilities
# ----------------------

def normalize_symbols(input):
    if isinstance(input, list):
        symbols = input
    else:
        symbols = str(input).split(",")

    symbols = list(dict.fromkeys(
        s.strip().upper()
        for s in symbols
        if s.strip()
    ))

    if not symbols:
        raise HTTPException(400, "No symbols provided")

    if len(symbols) > 25:
        raise HTTPException(400, "Too many symbols (max 25)")

    for symbol in symbols:
        if not re.match(r"^[A-Z.\-]+$", symbol):
            raise HTTPException(
                400,
                f"Invalid symbol format: {symbol}"
            )

    return symbols


def format_quote(q):
    return {
        "symbol": q.get("symbol"),
        "shortName": q.get("shortName"),
        "regularMarketPrice": q.get("regularMarketPrice"),
        "regularMarketChangePercent": q.get(
            "regularMarketChangePercent"
        ),
        "currency": q.get("currency"),
        "marketState": q.get("marketState"),
    }


async def get_formatted_quotes(symbols):
    symbols = normalize_symbols(symbols)

    ticker = Ticker(symbols)

    data = ticker.price

    if not isinstance(data, dict):
        return []

    results = []

    for symbol in symbols:
        quote = data.get(symbol)

        if quote and isinstance(quote, dict):
            quote["symbol"] = symbol
            results.append(format_quote(quote))

    return results


# ----------------------
# Routes
# ----------------------

@app.get("/stock/{symbol}")
async def get_stock(symbol: str):

    symbol = normalize_symbols(symbol)[0]

    cache_key = f"q:{symbol}"

    cached = get_cache(cache_key)

    if cached:
        return cached[0]

    result = await get_formatted_quotes([symbol])

    if not result:
        raise HTTPException(404, "Symbol not found")

    set_cache(cache_key, result, 5)

    return result[0]


@app.get("/stocks")
async def get_stocks(
    symbols: str = Query(...)
):

    symbols = normalize_symbols(symbols)

    cache_key = f"qs:{','.join(symbols)}"

    cached = get_cache(cache_key)

    if cached:
        return cached

    result = await get_formatted_quotes(symbols)

    set_cache(cache_key, result, 5)

    return result


@app.get("/health")
async def health():
    return {"ok": True}


# Run:
# uvicorn main:app --port 3001
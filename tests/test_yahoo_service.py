import pytest

from fastapi import HTTPException

from app.services.yahoo_service import normalize_symbols


def test_normalize_symbols():
    result = normalize_symbols("aapl, msft, goog")

    assert result == ["AAPL", "MSFT", "GOOG"]


def test_duplicate_symbols():
    result = normalize_symbols(["AAPL", "AAPL", "MSFT"])

    assert result == ["AAPL", "MSFT"]


def test_invalid_symbol():
    with pytest.raises(HTTPException):
        normalize_symbols(["AAPL123"])


def test_empty_symbols():
    with pytest.raises(HTTPException):
        normalize_symbols([])
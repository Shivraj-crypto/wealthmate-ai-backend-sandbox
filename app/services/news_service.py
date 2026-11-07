import os

import httpx

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import json

load_dotenv()

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

NEWS_URL = "https://api.massive.com/v2/reference/news"


def fetch_latest_news(limit=100, hours=48):

    if not MASSIVE_API_KEY:
        raise RuntimeError("MASSIVE_API_KEY is missing from .env")

    published_after = (
        datetime.now(timezone.utc) - timedelta(hours=hours)
    ).isoformat(timespec="seconds").replace("+00:00", "Z")

    params = {
        "published_utc.gte": published_after,
        "sort": "published_utc",
        "order": "desc",
        "limit": min(limit, 1000)
    }

    headers = {
        "Authorization": f"Bearer {MASSIVE_API_KEY}",
        "Accept": "application/json"
    }

    with httpx.Client(timeout=30) as client:

        response = client.get(
            NEWS_URL,
            params=params,
            headers=headers
        )

        response.raise_for_status()

        data = response.json()

    return data.get("results", [])


if __name__ == "__main__":

    articles = fetch_latest_news()

    print(f"Fetched {len(articles)} articles")

    print(json.dumps(articles[0], indent=4))
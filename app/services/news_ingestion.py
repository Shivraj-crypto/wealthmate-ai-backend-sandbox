from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import News, NewsStock, Stock
from .news_service import fetch_latest_news


def ingest_news():

    db: Session = SessionLocal()

    try:
        # Fetch latest news from Massive
        articles = fetch_latest_news(limit=100, hours=48)

        print(f"Fetched {len(articles)} articles from Massive")

        # Get existing article IDs to prevent duplicates
        external_ids = [
            article["id"]
            for article in articles
            if article.get("id")
        ]

        existing_ids = set()

        if external_ids:
            existing_ids = {
                row[0]
                for row in db.query(News.external_id)
                .filter(News.external_id.in_(external_ids))
                .all()
            }

        # Get stocks for ticker mapping
        stocks = db.query(Stock).all()

        stock_map = {
            stock.symbol.upper(): stock.id
            for stock in stocks
        }

        new_articles = []
        article_tickers = []
        seen_ids = set()

        for article in articles:

            external_id = article.get("id")
            title = article.get("title")
            published_utc = article.get("published_utc")

            if not external_id or not title or not published_utc:
                continue

            if external_id in existing_ids or external_id in seen_ids:
                continue

            seen_ids.add(external_id)

            # Convert publication timestamp
            published_at = datetime.fromisoformat(
                published_utc.replace("Z", "+00:00")
            )

            if published_at.tzinfo is None:
                published_at = published_at.replace(
                    tzinfo=timezone.utc
                )

            publisher = article.get("publisher") or {}

            tickers = article.get("tickers") or []
            keywords = article.get("keywords") or []
            insights = article.get("insights") or []

            news = News(
                external_id=external_id,
                title=title,
                author=article.get("author"),
                description=article.get("description"),
                article_url=article.get("article_url"),
                image_url=article.get("image_url"),
                publisher_name=publisher.get("name"),
                publisher_homepage_url=publisher.get("homepage_url"),
                publisher_logo_url=publisher.get("logo_url"),
                publisher_favicon_url=publisher.get("favicon_url"),
                published_at=published_at,
                fetched_at=datetime.now(timezone.utc),
                tickers=tickers,
                keywords=keywords,
                insights=insights
            )

            new_articles.append(news)

            article_tickers.append(
                (news, set(ticker.upper() for ticker in tickers))
            )

        # Insert new articles
        db.add_all(new_articles)
        db.flush()

        # Connect news articles to stocks
        news_stock_records = []

        for news, tickers in article_tickers:

            for ticker in tickers:

                stock_id = stock_map.get(ticker)

                if stock_id is not None:
                    news_stock_records.append(
                        NewsStock(
                            news_id=news.id,
                            stock_id=stock_id
                        )
                    )

        db.add_all(news_stock_records)

        # Delete articles older than 48 hours
        cutoff_date = datetime.now(timezone.utc) - timedelta(hours=48)

        deleted_count = (
            db.query(News)
            .filter(News.published_at < cutoff_date)
            .delete(synchronize_session=False)
        )

        db.commit()

        print(f"Successfully inserted {len(new_articles)} news articles")
        print(f"Created {len(news_stock_records)} stock associations")
        print(f"Deleted {deleted_count} expired articles")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    ingest_news()
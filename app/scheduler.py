from apscheduler.schedulers.background import BackgroundScheduler

from .services.stock_ingestion import (
    ingest_current_prices,
    ingest_historical_prices
)


scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        ingest_current_prices,
        "interval",
        minutes=30,
        id="current_prices",
        replace_existing=True
    )

    scheduler.add_job(
        ingest_historical_prices,
        "interval",
        days=1,
        id="historical_prices",
        replace_existing=True
    )

    scheduler.start()

    print("Scheduler started")


def stop_scheduler():
    scheduler.shutdown()

    print("Scheduler stopped")
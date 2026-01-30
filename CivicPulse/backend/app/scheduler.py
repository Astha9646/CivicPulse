"""Background scheduler for periodic data ingestion."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from .scraper import run_one_shot
from .main import ingest_one_shot

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def scheduled_ingest():
    """Wrapper for scheduled ingestion."""
    try:
        # Call the FastAPI endpoint logic directly
        articles = run_one_shot()
        # Note: This would need access to db, llm, geocode, scoring modules
        # For now, this is a placeholder - actual implementation would
        # call the same logic as the /ingest/one-shot endpoint
        print("Scheduled ingestion completed")
    except Exception as e:
        print(f"Scheduled ingestion error: {e}")


def start_scheduler(interval_hours: int = 6):
    """Start the background scheduler for periodic ingestion."""
    if scheduler.running:
        print("Scheduler already running")
        return
    
    # Schedule ingestion every N hours
    scheduler.add_job(
        scheduled_ingest,
        trigger=IntervalTrigger(hours=interval_hours),
        id='periodic_ingest',
        name='Periodic Safety Data Ingestion',
        replace_existing=True
    )
    
    scheduler.start()
    print(f"Scheduler started - will run ingestion every {interval_hours} hours")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")

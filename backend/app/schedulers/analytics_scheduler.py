
import logging

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.services.report_generator import generate_daily_reports


logger = logging.getLogger(__name__)

INDIA_TZ = ZoneInfo("Asia/Kolkata")

scheduler = BackgroundScheduler(timezone=INDIA_TZ)


def daily_analytics_job():
    db = SessionLocal()

    try:
        yesterday = (
            datetime.now(INDIA_TZ).date() - timedelta(days=1)
        )

        logger.info(
            "Starting analytics generation for %s",
            yesterday
        )

        generate_daily_reports(
            db=db,
            report_date=yesterday
        )

    except Exception:
        db.rollback()
        logger.exception("Daily analytics job failed")

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        daily_analytics_job,
        trigger=CronTrigger(
            hour=0,
            minute=5,
            timezone=INDIA_TZ
        ),
        id="daily_analytics_report",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=86400
    )

    if not scheduler.running:
        scheduler.start()

    logger.info("Analytics scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Analytics scheduler stopped")

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from generator import generate_newsletter, week_label
from database import save_newsletter


def run_newsletter_job():
    print("Newsletter job started...")
    try:
        parsed, raw = generate_newsletter()
        label = week_label()
        save_newsletter(
            week_label=label,
            stories=parsed["stories"],
            top_picks=parsed["top_picks"],
            raw_response=raw,
        )
        print(f"Newsletter saved: {label}")
    except Exception as e:
        print(f"Newsletter job failed: {e}")


def start_scheduler():
    central = pytz.timezone("US/Central")
    scheduler = BackgroundScheduler(timezone=central)
    scheduler.add_job(
        run_newsletter_job,
        trigger=CronTrigger(day_of_week="fri", hour=16, minute=0, timezone=central),
        id="weekly_newsletter",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started — newsletter runs every Friday at 4:00 PM CT")
    return scheduler

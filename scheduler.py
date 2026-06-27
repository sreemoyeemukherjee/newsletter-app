import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import database
import generator


def _run():
    data = generator.generate_newsletter(
        os.environ["ANTHROPIC_API_KEY"],
        os.environ["TAVILY_API_KEY"],
    )
    database.save(data)
    print(f"[scheduler] generated: {data.get('week')}")


def start() -> BackgroundScheduler:
    s = BackgroundScheduler()
    s.add_job(_run, CronTrigger(day_of_week="fri", hour=16, minute=0, timezone="America/Chicago"))
    s.start()
    return s

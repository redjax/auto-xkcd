from __future__ import annotations

from celery.schedules import crontab

## Check for new XKCD comic every hour
TASK_SCHEDULE_current_comic_check = {
    "hourly_current_comic_check": {
        "task": "celeryapp.celery_tasks.comic.task_current_comic",
        "schedule": crontab(hour="*", minute=0),
    }
}

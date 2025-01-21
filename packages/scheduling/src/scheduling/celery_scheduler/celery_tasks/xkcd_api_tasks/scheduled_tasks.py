from __future__ import annotations

from celery.schedules import crontab

## Check for new XKCD comic every hour
TASK_SCHEDULE_hourly_current_comic_check = {
    "hourly_current_comic_check": {
        "task": "request_and_save_current_comic",
        "schedule": crontab(hour="*", minute="0")
    }
}

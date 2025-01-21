from __future__ import annotations

from celery.schedules import crontab

## Check for new XKCD comic every hour
TASK_SCHEDULE_hourly_current_comic_check = {
    "hourly_current_comic_check": {
        "task": "request_and_save_current_comic",
        "schedule": crontab(hour="*", minute="0")
    }
}

## Check for new XKCD comic every minute
TASK_SCHEDULE_minutely_current_comic_check = {
    "minutely_current_comic_check": {
        "task": "request_and_save_current_comic",
        "schedule": crontab(minute="*")
    }
}

## Update current comic metadata in database every 5 minutes
TASK_SCHEDULE_5m_update_current_comic_metadata = {
    "5m_current_comic_metadata_update": {
        "task": "update_current_comic_metadata",
        "schedule": crontab(minute="*/5")
    }
}
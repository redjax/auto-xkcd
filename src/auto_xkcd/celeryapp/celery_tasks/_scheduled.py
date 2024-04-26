from celery.schedules import crontab
from datetime import timedelta

CELERY_IMPORTS = "celeryapp.celery_tasks"
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "celery.beat.PersistentScheduler"

CELERY_BEAT_SCHEDULE = {
    "refresh-current-comic": {
        "task": "celeryapp.celery_tasks.comic.task_current_comic",
        "schedule": timedelta(hours=1),
    }
}

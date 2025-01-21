from scheduling.celery_scheduler import celeryapp
from celery import current_app
from scheduling.celery_scheduler.celery_tasks.utils import get_celery_tasks_list


print(f"All Celery tasks: {get_celery_tasks_list(hide_celery_tasks=False)}")
print(f"Custom Celery tasks only: {get_celery_tasks_list()}")
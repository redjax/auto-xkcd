from scheduling.celery_scheduler import celeryapp
from celery import current_app
from scheduling.celery_scheduler.celery_tasks.utils import get_celery_tasks_list, execute_celery_task, watch_celery_task


print(f"All Celery tasks: {get_celery_tasks_list(hide_celery_tasks=False)}")
print(f"Custom Celery tasks only: {get_celery_tasks_list()}")

print("Executing task: adhoc-current-comic")

adhoc_current_comic_task = execute_celery_task("adhoc-current-comic", 150)
# print(f"Ad-hoc current comic request result ({type(adhoc_current_comic_task)}): {adhoc_current_comic_task}")
task_result = watch_celery_task(adhoc_current_comic_task, timeout=30)
# res = adhoc_current_comic_task.get(timeout=30)
# print(f"Task completed. Result: {res}")
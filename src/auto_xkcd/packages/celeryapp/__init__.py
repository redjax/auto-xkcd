# from .methods import current_comic
from ._celeryapp import app, check_task
from . import celery_tasks

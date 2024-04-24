from core.config import settings, celery_settings

from loguru import logger as log

if __name__ == "__main__":
    log.debug(f"Celery settings: {celery_settings}")

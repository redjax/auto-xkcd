from __future__ import annotations

from core.config import celery_settings, settings
from loguru import logger as log

if __name__ == "__main__":
    log.debug(f"Celery settings: {celery_settings}")

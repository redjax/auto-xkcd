from core.dependencies import settings
from _setup import base_app_setup

from loguru import logger as log


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

from __future__ import annotations

import argparse

from celery import Celery
import db_lib
from loguru import logger as log
from scheduling.celery_scheduler import (
    CelerySettings,
    celery_settings,
    celeryapp,
    check_task,
    start_celery,
    start_celery_beat,
    start_celery_worker,
)
from settings import APP_SETTINGS, CELERY_SETTINGS, DB_SETTINGS, LOGGING_SETTINGS
import setup

def parse_args():
    parser = argparse.ArgumentParser(
        description="Start the Celery application in worker or beat mode."
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        choices=["worker", "beat"],
        required=True,
        help="Mode to run the application: 'worker' or 'beat'."
    )
    return parser.parse_args()


def run(app: Celery, mode: str):
    log.debug(f"Celery mode: {mode}")
    
    log.debug(f"""
Database settings]
{DB_SETTINGS.as_dict()}

[Celery settings]
{CELERY_SETTINGS.as_dict()}

[Database connection string]
{db_lib.get_db_uri(drivername=DB_SETTINGS.get('DB_DRIVERNAME'), username=DB_SETTINGS.get('DB_USERNAME'), password=DB_SETTINGS.get('DB_PASSWORD'), host=DB_SETTINGS.get('DB_HOST'), port=DB_SETTINGS.get('DB_PORT'), database=DB_SETTINGS.get('DB_DATABASE'))}
""")
    
    log.debug(f"Celery settings class: {celery_settings}")
    
    try:
        start_celery.start(app=app, mode=mode)
    except Exception as e:
        log.error(f"Failed to start application: {e}")
        return False

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), log_fmt="basic", colorize=True)
    try:
        setup.setup_database()
    except Exception as exc:
        msg = f"({type(exc)}) Error setting up database. Details: {exc}"
        log.error(msg)
        
        raise
    
    args = parse_args()
    
    if not args.mode:
        log.error(f"[WARNING] Missing a --mode (-m). Please re-run with -m ['beat', 'worker'] (choose 1).")
        exit(1)
        
    try:
        run(app=celeryapp.app, mode=args.mode.lower())
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery in '{args.mode}' mode. Details: {exc}"
        log.error(msg)
        
        raise exc

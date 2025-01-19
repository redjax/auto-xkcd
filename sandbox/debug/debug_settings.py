from settings import (
    LOGGING_SETTINGS,
    DB_SETTINGS,
    APP_SETTINGS,
    CELERY_SETTINGS,
    FASTAPI_SETTINGS,
    UVICORN_SETTINGS,
)

from dynaconf import Dynaconf

LOOP_CONFS: list = [
    {"name": "logging", "obj": LOGGING_SETTINGS},
    {"name": "database", "obj": DB_SETTINGS},
    {"name": "app", "obj": APP_SETTINGS},
    {"name": "celery", "obj": CELERY_SETTINGS},
    {"name": "fastapi", "obj": FASTAPI_SETTINGS},
    {"name": "uvicorn", "obj": UVICORN_SETTINGS},
]


def dbg_settings_obj(obj: Dynaconf, name: str = "<Unnamed>"):
    print(f"\n[DEBUG] {name.title()} settings:\n{obj.as_dict()}")


for _conf in LOOP_CONFS:
    dbg_settings_obj(obj=_conf["obj"], name=_conf["name"])

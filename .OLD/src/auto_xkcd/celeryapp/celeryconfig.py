from __future__ import annotations

import typing as t

from dynaconf import Dynaconf
from pydantic import Field, ValidationError, computed_field, field_validator
from pydantic_settings import BaseSettings

DYNACONF_CELERY_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="CELERY",
    settings_files=["celery/settings.toml", "celery/.secrets.toml"],
)


class CelerySettings(BaseSettings):
    broker_host: str | None = Field(
        default=DYNACONF_CELERY_SETTINGS.CELERY_BROKER_HOST, env="RABBITMQ_HOST"
    )
    broker_port: t.Union[str, int] | None = Field(
        default=DYNACONF_CELERY_SETTINGS.CELERY_BROKER_PORT, env="RABBITMQ_PORT"
    )
    broker_user: str | None = Field(
        default=DYNACONF_CELERY_SETTINGS.CELERY_BROKER_USER, env="RABBITMQ_USER"
    )
    broker_password: str | None = Field(
        default=DYNACONF_CELERY_SETTINGS.CELERY_BROKER_PASS, env="RABBITMQ_PASS"
    )
    backend_host: str | None = Field(
        default=DYNACONF_CELERY_SETTINGS.CELERY_BACKEND_HOST, env="REDIS_HOST"
    )
    backend_port: t.Union[str, int] | None = Field(
        default=DYNACONF_CELERY_SETTINGS.CELERY_BACKEND_PORT, env="REDIS_PORT"
    )

    @field_validator("broker_port", "backend_port")
    def validate_port(cls, v) -> int:
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass

        return v

    @computed_field
    @property
    def broker_url(self) -> str:
        try:
            _url = f"amqp://{self.broker_user}:{self.broker_password}@{self.broker_host}:{self.broker_port}"
            return _url

        except Exception as exc:
            raise Exception(
                f"Unhandled exception building Celery broker URL. Details: {exc}"
            )

    @computed_field
    @property
    def backend_url(self) -> str:
        try:
            _url = f"redis://{self.backend_host}:{self.backend_port}/0"

            return _url

        except Exception as exc:
            raise Exception(
                f"Unhandled exception building Celery backend URL. Details: {exc}"
            )


celery_settings: CelerySettings = CelerySettings()

from __future__ import annotations

import typing as t

from loguru import logger as log
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)
from settings.celery_settings import CELERY_SETTINGS

def return_rabbitmq_url(
    username: str = CELERY_SETTINGS.get("CELERY_BROKER_USERNAME", default="guest"),
    password: str | None = CELERY_SETTINGS.get("CELERY_BROKER_PASSWORD", default=""),
    host: str = CELERY_SETTINGS.get("CELERY_BROKER_HOST", default="localhost"),
    port: str = CELERY_SETTINGS.get("CELERY_BROKER_PORT", default=5672),
    vhost: str | None = CELERY_SETTINGS.get("CELERY_BROKER_VHOST", default="/")
) -> str:
    """Return a string of the format amqp://<username>:<password>@<host>:<port> (or amqp://<username>@<host>:<port> for guest/passwordless auth) for RabbitMQ.
    
    Params:
        username (str): The username for database auth.
        password (str | None): The password for database auth.
        host (str | None): The host for database auth.
        port (str): The port for database auth.
        vhost (str | None): The vhost for database auth.
        
    Returns:
        (str): A string of the format amqp://<username>:<password>@<host>:<port>/<vhost>
    
    """
    if password:
        broker_url: str = f"amqp://{username}:{password}@{host}:{port}"
    else:
        broker_url: str = f"amqp://{username}:''@{host}:{port}"
        
    if vhost:
        broker_url += f"/{vhost}"
    else:
        broker_url += "/"

    # log.debug(f"Celery broker URL: {broker_url}")
    
    return broker_url


def return_redis_url(
    host: str = CELERY_SETTINGS.get('CELERY_BACKEND_HOST', default='localhost'),
    port: int | str = CELERY_SETTINGS.get('CELERY_BACKEND_PORT', default=6379),
    password: str | None = CELERY_SETTINGS.get("CELERY_BACKEND_PASSWORD", default="")
):
    if password:
        redis_url: str = f"redis://:{password}@{host}:{port}/0"
    else:
        redis_url: str = f"redis://{host}:{port}/0"
    
    # log.debug(f"Redis backend URL: {redis_url}")
    
    return redis_url


class CelerySettings(BaseModel):
    broker_host: str = Field(default=CELERY_SETTINGS.get("CELERY_BROKER_HOST", default="localhost"))
    broker_port: t.Union[int, str] = Field(default=CELERY_SETTINGS.get("CELERY_BROKER_PORT", default=5672))
    broker_username: str = Field(default=CELERY_SETTINGS.get("CELERY_BROKER_USERNAME", default="guest"))
    broker_password: str | None = Field(default=CELERY_SETTINGS.get("CELERY_BROKER_PASSWORD", default=""))
    broker_vhost: str = Field(default=CELERY_SETTINGS.get("CELERY_BROKER_VHOST", default="/"))
    backend_host: str | None = Field(default=CELERY_SETTINGS.get("CELERY_BACKEND_HOST", default="localhost"))
    backend_port: t.Union[int, str] = Field(default=CELERY_SETTINGS.get("CELERY_BACKEND_PORT", default=6379))
    
    @field_validator("broker_port", "backend_port")
    def validate_port(cls, v) -> int:
        ## This line is so vulture stops complaining about cls not being used
        if not cls:
            pass
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass

        return v

    @computed_field
    @property
    def broker_url(self) -> str:
        if self.broker_password:
            broker_url: str = f"amqp://{self.broker_username}:{self.broker_password}@{self.broker_host}:{self.broker_port}"
        else:
            broker_url: str = f"amqp://{self.broker_username}:''@{self.broker_host}:{self.broker_port}"
            
        if self.broker_vhost:
            broker_url += f"/{self.broker_vhost}"
        else:
            broker_url += "/"
        
        return broker_url

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
# log.debug(f"celery_settings class object: {celery_settings}")
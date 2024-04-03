from __future__ import annotations

from pathlib import Path
import typing as t

from pydantic import Field, ValidationError, computed_field, field_validator
from pydantic_settings import BaseSettings

## Uncomment if adding a database config
import sqlalchemy as sa
import sqlalchemy.orm as so

## Uncomment if adding a database config
valid_db_types: list[str] = ["sqlite", "postgres", "mssql"]


class AppSettings(BaseSettings):
    env: str = Field(default="prod", env="ENV")
    container_env: bool = Field(default=False, env="CONTAINER_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    logs_dir: t.Union[str, Path] = Field(default="logs", env="LOGS_DIR")

    @field_validator("logs_dir")
    def validate_logs_dir(cls, v) -> Path:
        if isinstance(v, str):
            if "~" in v:
                return Path(v).expanduser()
            else:
                return Path(v)

        if isinstance(v, Path):
            if "~" in f"{v}":
                return v.expanduser()
            else:
                return v

        raise ValidationError


## Uncomment if you're configuring a database for the app
class DBSettings(BaseSettings):
    type: str = Field(default="sqlite", env="DB_TYPE")
    drivername: str = Field(default="sqlite+pysqlite", env="DB_DRIVERNAME")
    username: str | None = Field(default=None, env="DB_USERNAME")
    password: str | None = Field(default=None, env="DB_PASSWORD", repr=False)
    host: str | None = Field(default=None, env="DB_HOST")
    port: t.Union[str, int, None] = Field(default=None, env="DB_PORT")
    database: str = Field(default="auto-xkcd.sqlite", env="DB_DATABASE")
    echo: bool = Field(default=True, env="DB_ECHO")

    @field_validator("port")
    def validate_db_port(cls, v) -> int:
        if v is None or v == "":
            return None
        elif isinstance(v, int):
            return v
        elif isinstance(v, str):
            return int(v)
        else:
            raise ValidationError

    def get_db_uri(self) -> sa.URL:
        try:
            _uri: sa.URL = sa.URL.create(
                drivername=self.drivername,
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
            )

            return _uri

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting SQLAlchemy database URL. Details: {exc}"
            )
            raise msg

    def get_engine(self) -> sa.Engine:
        assert self.get_db_uri() is not None, ValueError("db_uri is not None")
        assert isinstance(self.get_db_uri(), sa.URL), TypeError(
            f"db_uri must be of type sqlalchemy.URL. Got type: ({type(self.db_uri)})"
        )

        try:
            engine: sa.Engine = sa.create_engine(
                url=self.get_db_uri().render_as_string(hide_password=False),
                echo=self.echo,
            )

            return engine
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting database engine. Details: {exc}"
            )

            raise msg

    def get_session_pool(self) -> so.sessionmaker[so.Session]:
        engine: sa.Engine = self.get_engine()
        assert engine is not None, ValueError("engine cannot be None")
        assert isinstance(engine, sa.Engine), TypeError(
            f"engine must be of type sqlalchemy.Engine. Got type: ({type(engine)})"
        )

        session_pool: so.sessionmaker[so.Session] = so.sessionmaker(bind=engine)

        return session_pool


class MinioSettings(BaseSettings):
    address: str = Field(default=None, env="MINIO_ADDRESS")
    port: int = Field(default=9000, env="MINIO_PORT")
    secure: bool = Field(default=True, env="MINIO_HTTPS")
    username: str = Field(default=None, env="MINIO_USERNAME")
    password: str = Field(default=None, env="MINIO_PASSWORD", repr=False)
    access_key: str = Field(default=None, env="MINIO_ACCESS_KEY")
    access_secret: str = Field(default=None, env="MINIO_ACCESS_SECRET", repr=False)

    @property
    def endpoint(self) -> str:
        return f"{self.address}:{self.port}"


class TelegramSettings(BaseSettings):
    bot_token: str | None = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    bot_username: str | None = Field(default=None, env="TELEGRAM_BOT_USERNAME")

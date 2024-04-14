from __future__ import annotations

from pathlib import Path
import typing as t

from pydantic import Field, ValidationError, computed_field, field_validator
from pydantic_settings import BaseSettings

## Uncomment if adding a database config
import sqlalchemy as sa
import sqlalchemy.orm as so

from dynaconf import Dynaconf

## Uncomment if adding a database config
valid_db_types: list[str] = ["sqlite", "postgres", "mssql"]

DYNACONF_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
)
DYNACONF_DB_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="DB",
    settings_files=["db/settings.toml", "db/.secrets.toml"],
)
# DYNACONF_MINIO_SETTINGS: Dynaconf = Dynaconf(
#     environments=True,
#     envvar_prefix="MINIO",
#     settings_files=["minio/settings.toml", "minio/.secrets.toml"],
# )


class AppSettings(BaseSettings):
    """Store application configuration values.

    Params:
        env (str): Usually `prod` or `dev`.
        container_env (bool): If running in a container, you can set an env variable
            `DYNACONF_CONTAINER_ENV=True` to indicate the app is running in a container.
            This can be useful for controlling certain behaviors when running in a container.
        log_level (str): Control logging level. i.e. `"INFO"`, `"DEBUG"`, `"WARNING"`, etc
        logs_dir (str|Path): The directory where logs will be stored, if file logging is enabled.
    """

    env: str = Field(default=DYNACONF_SETTINGS.ENV, env="ENV")
    container_env: bool = Field(
        default=DYNACONF_SETTINGS.CONTAINER_ENV, env="CONTAINER_ENV"
    )
    log_level: str = Field(default=DYNACONF_SETTINGS.LOG_LEVEL, env="LOG_LEVEL")
    logs_dir: t.Union[str, Path] = Field(
        default=DYNACONF_SETTINGS.LOGS_DIR, env="LOGS_DIR"
    )

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

    @field_validator("log_level")
    def validate_log_level(cls, v) -> str:
        if isinstance(v, str):
            return v.upper()

        raise ValidationError


## Uncomment if you're configuring a database for the app
class DBSettings(BaseSettings):
    """Store database configuration values.

    Params:
        type (str): The database type, i.e. `'sqlite'`.
        drivername (str): The `sqlalchemy` driver name, i.e. `'sqlite+pysqlite'`.
        username (str|None): The database user's username.
        password (str|None): The database user's password.
        host (str|None): The database host address.
        port (str|int|None): The database host's port.
        database (str): The name of the database to connect to. For SQLite, use the path to the file,
            i.e. `db/app.sqlite`.
        echo (bool): If `True`, the SQLAlchemy `Engine` will echo SQL queries to the CLI, and will create tables
            that do not exist (if possible).

    """

    type: str = Field(
        default=DYNACONF_DB_SETTINGS.DB_TYPE,
        description="The type of database this configuration defines.",
        env="DB_TYPE",
    )
    drivername: str = Field(
        default=DYNACONF_DB_SETTINGS.DB_DRIVERNAME,
        description="The SQLAlchemy drivername string.",
        env="DB_DRIVERNAME",
    )
    username: str | None = Field(
        default=DYNACONF_DB_SETTINGS.DB_USERNAME,
        description="The username for database authentication.",
        env="DB_USERNAME",
    )
    password: str | None = Field(
        default=DYNACONF_DB_SETTINGS.DB_PASSWORD,
        description="The pasword for database authentication.",
        env="DB_PASSWORD",
        repr=False,
    )
    host: str | None = Field(
        default=DYNACONF_DB_SETTINGS.DB_HOST,
        description="The host address of the database server.",
        env="DB_HOST",
    )
    port: t.Union[str, int, None] = Field(
        default=DYNACONF_DB_SETTINGS.DB_PORT,
        description="The port of the database server.",
        env="DB_PORT",
    )
    database: str = Field(
        default=DYNACONF_DB_SETTINGS.DB_DATABASE,
        description="The database to connect to.",
        env="DB_DATABASE",
    )
    echo: bool = Field(
        default=DYNACONF_DB_SETTINGS.DB_ECHO,
        description="Configure the SQLAlchemy `Engine`'s echo truthiness.",
        env="DB_ECHO",
    )

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
        """Build & return a SQLAlchemy `Engine`.

        Returns:
            `sqlalchemy.Engine`: A SQLAlchemy `Engine` instance.

        """
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
        """Configure a session pool using class's SQLAlchemy `Engine`.

        Returns:
            (sqlalchemy.orm.sessionmaker): A SQLAlchemy `Session` pool for database connections.

        """
        engine: sa.Engine = self.get_engine()
        assert engine is not None, ValueError("engine cannot be None")
        assert isinstance(engine, sa.Engine), TypeError(
            f"engine must be of type sqlalchemy.Engine. Got type: ({type(engine)})"
        )

        session_pool: so.sessionmaker[so.Session] = so.sessionmaker(bind=engine)

        return session_pool


class MinioSettings(BaseSettings):
    """Store minio configuration values.

    Params:
        address (str): The address of the minio server.
        port (int): The port of the minio server.
        secure (bool): Whether or not to connect over HTTPS.
        username (str): The username to authenticate with.
        password (str): The password to authenticate with.
        access_key (str): The API key value.
        access_secret (str): The  API key secret.
    """

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
    """Configuration values for Telegram messaging.

    Params:
        bot_token (str): The Telegram bot's token.
        bot_username( str): The Telegram bot's username.
    """

    bot_token: str | None = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    bot_username: str | None = Field(default=None, env="TELEGRAM_BOT_USERNAME")


settings: AppSettings = AppSettings()

db_settings: DBSettings = DBSettings()

telegram_settings: TelegramSettings = TelegramSettings()

# minio_settings: MinioSettings = MinioSettings(
#     address=DYNACONF_MINIO_SETTINGS.MINIO_ADDRESS,
#     port=DYNACONF_MINIO_SETTINGS.MINIO_PORT,
#     secure=DYNACONF_MINIO_SETTINGS.MINIO_HTTPS,
#     username=DYNACONF_MINIO_SETTINGS.MINIO_USERNAME,
#     password=DYNACONF_MINIO_SETTINGS.MINIO_PASSWORD,
#     access_key=DYNACONF_MINIO_SETTINGS.MINIO_ACCESS_KEY,
#     access_secret=DYNACONF_MINIO_SETTINGS.MINIO_ACCESS_SECRET,
#     echo=DYNACONF_DB_SETTINGS.DB_ECHO,
# )

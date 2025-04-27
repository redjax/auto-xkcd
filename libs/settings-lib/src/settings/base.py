from __future__ import annotations

from dynaconf import Dynaconf

__all__ = ["SETTINGS", "get_namespace"]

## Initialize Dynaconf object with all configurations
SETTINGS = Dynaconf(
    environments=True,
    settings_files=[
        "settings.toml",
        ".secrets.toml",
        "config/**/settings.toml",
        "config/**/.secrets.toml",
    ],
)


def get_namespace(namespace: str) -> Dynaconf:
    """Return a Dyanconf object scoped to a namespace.

    Description:
        Uses the global SETTINGS Dynaconf object to return only the environment/namespace.
        In your settings.toml/.secrets.toml, separate your configurations by domain, i.e.:

        ```toml
        [logging]
        log_level = "INFO"

        [api]
        url = "http://127.0.0.1"
        port = 8000
        ```

        Now you can use .get_namespace() to return a Dynaconf object, instead of declaring a new object
        for every configuration domain.

    Params:
        namespace (str): The name of a `[namespace]` in your settings.toml/.secrets.toml, i.e. 'logging' or 'api'.

    Returns:
        (Dynaconf): A scoped Dynaconf settings object.

    """
    try:
        scoped_settings = SETTINGS.from_env(namespace)

        return scoped_settings
    except Exception as exc:
        raise Exception(
            f"Error scoping Dynaconf settings to namespace '{namespace}'. Details: {exc}"
        )

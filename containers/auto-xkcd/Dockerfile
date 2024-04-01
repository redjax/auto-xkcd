FROM python:3.11-slim as base

## Set ENV variables to control Python/pip behavior inside container
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    ## Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

FROM base AS build

WORKDIR /app

COPY requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt

## Use target: dev to build this step
FROM build AS dev

ENV ENV_FOR_DYNACONF=dev
## Tell Dynaconf to always load from the environment first while in the container
ENV DYNACONF_ALWAYS_LOAD_ENV_VARS=True

WORKDIR /app
COPY ../../src .

############
# Optional #
############
# Export ports, set an entrypoint/CMD, etc
#   Note: This is normally handled by your orchestrator (docker-compose, Azure Container App, etc)

# EXPOSE 5000
CMD ["python", "main.py"]

## Use target: prod to build this step
FROM build AS prod

ENV ENV_FOR_DYNACONF=prod
## Tell Dynaconf to always load from the environment first while in the container
ENV DYNACONF_ALWAYS_LOAD_ENV_VARS=True

WORKDIR /app
COPY ../../src .

############
# Optional #
############
# Export ports, set an entrypoint/CMD, etc
#   Note: This is normally handled by your orchestrator (docker-compose, Azure Container App, etc)

# EXPOSE 5000
CMD ["python", "main.py"]
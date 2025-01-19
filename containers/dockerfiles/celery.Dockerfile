ARG UV_BASE=${UV_IMAGE_VER:-0.5.9}
ARG PYTHON_BASE=${PYTHON_IMG_VER:-3.11-slim}

FROM ghcr.io/astral-sh/uv:${UV_BASE} AS uv
FROM python:${PYTHON_BASE} AS base

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        iputils-ping \
        libmemcached-dev \
        zlib1g-dev \
        curl \
        ca-certificates \
        software-properties-common \
        apt-transport-https \
        sudo \
        postgresql \
        python3-psycopg2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN mkdir -p /project /auto-xkcd/db /auto-xkcd/logs

FROM base AS stage

WORKDIR /project

COPY --from=base /auto-xkcd /auto-xkcd

COPY pyproject.toml uv.lock README.md ./

## Copy monorepo domains
COPY applications/ applications/
COPY libs/ libs/
COPY packages/ packages/
COPY scripts/ scripts/
COPY src/ src/

FROM stage AS build

COPY --from=stage /project /project
COPY --from=stage /auto-xkcd /auto-xkcd
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

## Build project in container
RUN uv sync --all-extras \
    && uv build

FROM build AS celery_beat

COPY --from=build /project /project
COPY --from=build /auto-xkcd /auto-xkcd
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "beat"]

FROM build AS celery_worker

COPY --from=build /project /project
COPY --from=build /auto-xkcd /auto-xkcd

WORKDIR /project

CMD ["uv", "run", "scripts/celery/start_celery.py", "-m", "worker"]

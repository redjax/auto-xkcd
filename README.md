# Auto XKCD <!-- omit in toc -->

<!-- Repo image -->
<p align="center">
  <a href="https://github.com/redjax/auto-xkcd">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://imgs.xkcd.com/comics/shouldnt_be_hard.png">
      <img src="https://imgs.xkcd.com/comics/shouldnt_be_hard.png" height="200">
    </picture>
  </a>
</p>

<!-- Git Badges -->
<p align="center">
  <a href="https://github.com/redjax/auto-xkcd">
    <img alt="Created At" src="https://img.shields.io/github/created-at/redjax/auto-xkcd">
  </a>
  <a href="https://github.com/redjax/auto-xkcd/commit">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/redjax/auto-xkcd">
  </a>
  <a href="https://github.com/redjax/auto-xkcd/commit">
    <img alt="Commits this year" src="https://img.shields.io/github/commit-activity/y/redjax/auto-xkcd">
  </a>
  <a href="https://github.com/redjax/auto-xkcd">
    <img alt="Repo size" src="https://img.shields.io/github/repo-size/redjax/auto-xkcd">
  </a>
  <!-- ![GitHub Latest Release](https://img.shields.io/github/release-date/redjax/auto-xkcd) -->
  <!-- ![GitHub commits since latest release](https://img.shields.io/github/commits-since/redjax/auto-xkcd/latest) -->
  <!-- ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/redjax/auto-xkcd/tests.yml) -->
</p>

---

Python monorepo for interacting with the [XKCD JSON API](https://xkcd.com/json.html).

## Description <!-- omit in toc -->

This repository is a monorepo, with code split up into applications, libraries, and packages. The script has a number of entrypoints in the [`sandbox`](./sandbox/) and [`scripts`](./scripts/) directories. The sandbox is for prototyping, and the scripts path has script entrypoints for starting different portions of the app.

This project makes requests to the XKCD API, and can download comic metadata and images. For development, the app uses a SQLite database, while the "production" version uses a Postgres container in the [production docker compose stack](./containers/compose.yml).

Background tasks are handled with [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html).

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Monorepo Layout](#monorepo-layout)
- [Setup](#setup)
  - [Requirements](#requirements)
  - [Env Setup](#env-setup)
    - [Using the messaging stack](#using-the-messaging-stack)
    - [Using the dev.compose.yml or compose.yml stacks](#using-the-devcomposeyml-or-composeyml-stacks)
- [Usage](#usage)
  - [Run the celery scheduler](#run-the-celery-scheduler)
    - [Outside of Docker container](#outside-of-docker-container)
    - [Inside Docker container](#inside-docker-container)
- [Links](#links)

## Monorepo Layout

*note: This may not be completely up to date, if I haven't finished documenting a new section of the app. You can always click through paths in the repository to see what's inside 🙂*

The project builds code from different areas of the app, depending on where the code is called. Code lives in one of the following paths:

- [applications/](./applications/)
  - Combine functionality of [libraries](./libs/) and [packages](./packages/) into applications like a [Cyclopts](https://cyclopts.readthedocs.io/) CLI for the repository, or a [FastAPI](https://fastapi.tiangolo.com/) backend.
  - Applications are a "final state" for assembled code components in this repository.
- [libs/](./libs/)
  - Library packages that are not tied to any particular package in the repository.
  - Include things like a lower-level/generic [HTTP request controller](./libs/http-lib/), or the [`core_utils` library](./libs/coreutils-lib/) that provides shareable code any other package/application can import.
- [packages/](./packages/)
  - Packages handle logical groups of code functionality.
  - For example, all [Pydantic](https://docs.pydantic.dev/latest/) schemas and [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/) database model classes are declared in one of the [`domain`](./packages/domain/) modules.
  - Packages are meant to be isolated from each other, and can be imported & combined into [applications](./applications/).
- [scripts/](./scripts/)
  - Entrypoint scripts for the app or repository.
  - A script can import [packages](./packages/) and [libraries](./libs/), or can call an [application's](./applications/) entrypoint.
  - For example, the [`start_celery.py`](./scripts/celery/start_celery.py) script (which takes an arg `-m <celery mode>`) calls the [`scheduling` package's `start_celery.py`](./packages/scheduling/src/scheduling/celery_scheduler/start_celery.py), piping the user's arguments in and starting either a Celery worker or the Celery Beat schedule.
    - Scripts can also be shell scripts for tasks affecting the whole repository, like the [`prune_git_branches.sh`](./scripts/prune_git_branches.sh) script, which deletes local branches that have been removed from the remote.

## Setup

### Requirements

- [`uv`](https://docs.astral.sh/uv): The monorepo is managed with [`uv` workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/), and the tool is required to build & run most of it.
  - I may work on a way to export requirements so the project is installable with `pip`/`virtualenv`, but no promises...`uv` is very nice and you should try it!
- (Optional) Python
  - If you install `uv`, it can [manage your Python install for you](https://docs.astral.sh/uv/guides/install-python/), meaning you don't have to have Python installed in this project to launch it with `uv`!
- Docker & Docker Compose
  - The script depends on a number of containers for the Celery scheduler.
  - The [containers/ directory](./containers/) defines a number of stacks & custom Dockerfiles to run the project in a containerized environment.

### Env Setup

Most of the main functionality of this application requires Celery, which depends on a [`rabbitmq`]() and [`redis`]() container (defined in the [messaging `compose.yml`](./containers/messaging.compose.yml)). As such, start with setting up the "messaging" stack. If you want to run the Celery worker & Beat scheduler in containers, use the [`dev.compose.yml` stack](./containers/dev.compose.yml) for local development, or the [`compose.yml` stack](./containers/compose.yml) for "production"/live runtimes.

When running any part of the script outside of a Docker container (i.e. on the local host), you need to also give it configurations by modifying settings files in the [config/ directory](./config/).

- Copy `./config/settings.toml` -> `./config/settings.local.toml`
  - These are the "main" settings for the app, like the `LOG_LEVEL` and `TZ`
- Copy `./celery/settings.toml` -> `./celery/settings.local.toml`
  - These are the non-secret configurations for celery, like the rabbitmq or redis hostname and username, but not the password.
- Copy `./celery/.secrets.toml` -> `./celery/.secrets.local.toml`
  - These are secrets for the Celery app, like a rabbitmq or redis password.
- Copy `./database/settings.toml` -> `./database/settings.local.toml`
  - These are the non-secret configurations for the database client, like the database hostname and `DB_TYPE` (which tells the app what type of database it's using, i.e. `sqlite`, `postgres`, `mysql`, etc)

If you will be running a FastAPI backend, you should also copy & edit the [fastapi](./config/fastapi/) and [uvicorn](./config/uvicorn/) settings files.

#### Using the messaging stack

The [messaging stack](./containers/messaging.compose.yml) runs a redis and rabbitmq container. The configuration for this stack is stored in the [containers/envs/ path](./containers/envs/). The `messaging.compose.yml` stack looks for its environment in the [containers/envs/dev/messaging.env](./containers/envs/dev/messaging.env.example) file.

Copy `containers/envs/dev/messaging.env.example` -> `containers/envs/dev/messaging.env`. You can run the app as-is, or change any of the values within. For example, if you are already running a service on redis's `6379`, you could change the port by setting `REDIS_PORT=<new port>`.

#### Using the dev.compose.yml or compose.yml stacks

The [`dev.compose.yml`](./containers/dev.compose.yml) and [`compose.yml`](./containers/compose.yml) stacks both run the Celery worker/Beat scheduler in containers.

Like the [messaging stack](#using-the-messaging-stack), you need to copy the example environment files and edit them. The `dev.compose.yml` file looks in the containers/envs/dev/ path for env files, and the `compose.yml` file looks in containers/envs/prod/.

- Copy `./containers/envs/<env>/app.env.example` -> `./containers/envs/<env>/app.env`
  - Edit the values in this path to set things like the `LOG_LEVEL` and `TZ`.
- Copy `./containers/envs/<env>/messaging.env.example` -> `./containers/envs/<env>/messaging.env`
  - Edit values for redis and rabbitmq.

## Usage

...

### Run the celery scheduler

#### Outside of Docker container

*!! If you are calling the [`start_celery.py` script](./scripts/celery/start_celery.py) outside of a container, you must give the app configurations using the [config/ directory](./config/), as well as copying & editing the [env files](./containers/envs/). !!*

- Start the [`messaging.compose.yml`](./containers/messaging.compose.yml) stack to bring up just the redis and rabbitmq containers
  - `$ docker compose -f ./containers/messaging.compose.yml up -d`
  - You can check the redis or rabbitmq container's logs with:
    - `$ docker compose -f ./containers/messaging.compose.yml logs -f [rabbitmq, redis]`
- Start the Celery Beat scheduler
  - `$ uv run scripts/celery/start_celery.py -m beat`
- In a new terminal window/session, start the Celery worker
  - `$ uv run scripts/celery/start_celery.py -m worker`

#### Inside Docker container

...

## Links

- [XKCD web API](https://xkcd.com/json.html)

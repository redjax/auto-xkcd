# auto-xkcd

Query the [XKCD API](https://xkcd.com/json.html).

## Description

This is a learning project. The [XKCD web comic](https://www.xkcd.com) provides a [JSON API](https://xkcd.com/0/json.html) for requesting comic strips. This app, while being intentionally over-engineered, demonstrates some technologies I want to understand better, and serves as a showcase/reference for tools like FastAPI, rabbitMQ, minio, Redis, and more.

The main app consists of:

- An API ([FastAPI](https://fastapi.tiangolo.com))
- A SQLite database for storing comics, images, and metadata
- A [rabbitMQ](https://www.rabbitmq.com) messaging service
- A [Redis](https://redis.io) backend for rabbitMQ job results
  - I am sticking with Redis for now, despite their [recent license change](https://arstechnica.com/information-technology/2024/04/redis-license-change-and-forking-are-a-mess-that-everybody-can-feel-bad-about/). I have not tested running Celery with a different key/value store.
  - I would like to eventually switch to [Valkey](https://github.com/valkey-io/valkey)
- A [Celery](https://docs.celeryq.dev/en/stable/index.html) app to handle background/async tasks with rabbitMQ and Redis

The API handles requests to the XKCD API, with a rate limit of 1 request per 5 seconds (to avoid sending a ton of requests to the wonderful Randall Monroe...he doesn't deserve that) when multiple comics are requested. In the case of multiple comic requests, requests are broken into "partitions" when >15 comics are requested at once, and the requests are run as background tasks with rabbitMQ; the results can be retrieved with the FastAPI app, which pulls the results from the Redis backend.

## Usage

- Edit environment variables in [`./containers/env_files`](./containers/env_files/)
- From the project root, run `python dockerctl.py`
  - Because the `docker-compose.yml` and `.env` files are nested in `./containers`, it's annoying having to prepend `-f ./containers/docker-compose.[dev|prod].yml` to ever command.
  - The `dockerctl.py` script uses the cross-platform `subprocess` module to run Docker commands on your behalf. Follow the prompts to control Docker operations

- Visit the API, rabbitMQ management console, or Redis commander using the following (assumes default ports, substitute your own if you change them):

| service                     |  port |
| :-------------------------- | ----: |
| FastAPI                     |  8000 |
| rabbitMQ Management Console | 15672 |
| redis-commander webUI       |  8081 |

## Links

- [minio-py Github](https://github.com/minio/minio-py)
- [minio-py examples](https://github.com/minio/minio-py/tree/master/examples)
- [minio Python API client reference](https://min.io/docs/minio/linux/developers/python/API.html)
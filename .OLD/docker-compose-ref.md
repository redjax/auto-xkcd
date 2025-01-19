# auto-xkcd docker-compose reference

This project nests Docker files under `containers/`. Below is a reference table for commands, adding the correct path to an environment's `$ docker compose` command.

## Dev

### Build

```shell
docker compose -f containers/docker-compose.dev.yml build
```

### Run

```shell
docker compose -f containers/docker-compose.dev.yml up -d
```

### Get Logs

```shell
docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd
```

### Build & Run

```shell
docker compose -f containers/docker-compose.dev.yml up -d --build
```

### Run & Get Logs

```shell
docker compose -f containers/docker-compose.dev.yml up -d && docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd
```

### Build, Run, & Get Logs

```shell
docker compose -f containers/docker-compose.dev.yml up -d --build && docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd
```

## Prod

### Build

```shell
docker compose -f containers/docker-compose.dev.yml build

## Or, skipping cache & forcing full rebuild
docker compose -f containers/docker-compose.dev.yml build --no-cache
```

### Run

```shell
docker compose -f containers/docker-compose.dev.yml up -d
```

### Get Logs

```shell
docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd
```

### Build & Run

```shell
docker compose -f containers/docker-compose.dev.yml up -d --build
```

### Run & Get Logs

```shell
docker compose -f containers/docker-compose.dev.yml up -d && docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd
```

### Build, Run, & Get Logs

```shell
docker compose -f containers/docker-compose.dev.yml up -d --build && docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd
```

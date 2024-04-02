#!/bin/bash
echo "Building container"
docker compose -f containers/docker-compose.dev.yml up -d --build

echo "Getting container logs"
docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd

#!/bin/bash
echo "Building container"
docker compose -f containers/docker-compose.dev.yml build --no-cache

echo "Starting container"
docker compose -f containers/docker-compose.dev.yml up -d --force-recreate
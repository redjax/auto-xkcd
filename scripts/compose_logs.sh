#!/bin/bash
echo "Getting container logs"
docker compose -f containers/docker-compose.dev.yml logs -f autoxkcd

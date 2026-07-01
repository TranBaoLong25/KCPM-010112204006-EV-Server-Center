#!/usr/bin/env bash
# Simple deploy script for booking-service
# Intended to run on the deployment server. Pulls latest image and restarts docker-compose.

set -euo pipefail

# Configuration - edit as needed
IMAGE_NAME="${DOCKERHUB_USERNAME:-booking-service}" # will be overridden by env
IMAGE_TAG="${GITHUB_SHA:-latest}"
COMPOSE_FILE="/opt/booking/docker-compose.yml"
SERVICE_NAME="booking-service" # name of service in compose

echo "Pulling image ${IMAGE_NAME}:${IMAGE_TAG}..."
docker pull ${IMAGE_NAME}:${IMAGE_TAG}

echo "Tagging image as ${SERVICE_NAME}:latest"
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${SERVICE_NAME}:latest

echo "Bring up with docker-compose (${COMPOSE_FILE})"
docker-compose -f "${COMPOSE_FILE}" up -d --no-deps --build ${SERVICE_NAME}

echo "Prune dangling images"
docker image prune -f

echo "Deployed ${SERVICE_NAME} with image ${IMAGE_NAME}:${IMAGE_TAG}"
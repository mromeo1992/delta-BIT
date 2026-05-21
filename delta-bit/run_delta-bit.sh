#!/bin/bash
export HOST_UID=$(id -u)
export HOST_GID=$(id -g)


if command -v nvidia-smi &> /dev/null; then
    echo "GPU detected → running GPU mode"
    docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --remove-orphans
else
    echo "No GPU → running CPU mode"
    docker compose up --remove-orphans
fi
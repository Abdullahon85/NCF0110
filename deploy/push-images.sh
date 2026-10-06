#!/bin/sh
# Build the backend and frontend images and push them to a Docker registry.
# Usage (from the repository root): ./deploy/push-images.sh registry.example.uz:5000 [tag]
set -e
REGISTRY="${1:?usage: $0 <registry-host:port> [tag]}"
TAG="${2:-$(git rev-parse --short HEAD)}"
cd "$(dirname "$0")/.."

# docker compose needs an .env file to exist; build itself uses no secrets.
[ -f .env ] || cp .env.docker.example .env

docker login "$REGISTRY"
REGISTRY="$REGISTRY" TAG="$TAG" docker compose build backend frontend
for name in ncf-backend ncf-frontend; do
    docker tag "$REGISTRY/$name:$TAG" "$REGISTRY/$name:latest"
    docker push "$REGISTRY/$name:$TAG"
    docker push "$REGISTRY/$name:latest"
done
echo "Pushed $REGISTRY/ncf-backend and ncf-frontend with tags $TAG and latest."

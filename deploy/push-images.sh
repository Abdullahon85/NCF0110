#!/bin/sh
# Build the single NCF image (site + API + SQLite) and push it to a Docker registry.
# Usage (from the repository root): ./deploy/push-images.sh registry.example.uz:5000 [tag]
set -e
REGISTRY="${1:?usage: $0 <registry-host:port> [tag]}"
TAG="${2:-$(git rev-parse --short HEAD)}"
cd "$(dirname "$0")/.."

# docker compose needs an .env file to exist; the build itself uses no secrets.
[ -f .env ] || cp .env.docker.example .env

docker login "$REGISTRY"
REGISTRY="$REGISTRY" TAG="$TAG" docker compose build ncf
docker tag "$REGISTRY/ncf:$TAG" "$REGISTRY/ncf:latest"
docker push "$REGISTRY/ncf:$TAG"
docker push "$REGISTRY/ncf:latest"
echo "Pushed $REGISTRY/ncf with tags $TAG and latest."

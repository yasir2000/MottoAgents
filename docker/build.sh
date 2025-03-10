#!/bin/bash
set -e

# Configuration
IMAGE="yasir2000/mottoagents"
VERSION=1.0
DOCKERFILE="docker/Dockerfile"

# Enable BuildKit
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain
export BUILDKIT_CONFIG=docker/docker-buildkit.toml

# Clean up any existing containers/images
echo "Cleaning up old containers and images..."
docker ps -a | grep ${IMAGE} | awk '{print $1}' | xargs -r docker rm -f
docker images | grep ${IMAGE} | awk '{print $3}' | xargs -r docker rmi -f

# Clean BuildKit cache
echo "Cleaning BuildKit cache..."
docker builder prune -af

# Build the image with no cache
echo "Building ${IMAGE}:${VERSION} with no cache..."
docker build \
    --progress=plain \
    --no-cache \
    --pull \
    --force-rm \
    -f ${DOCKERFILE} \
    -t "${IMAGE}:${VERSION}" \
    .

if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi
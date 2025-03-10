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

# Build the image
echo "Building ${IMAGE}:${VERSION}..."
docker build \
    --progress=plain \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg MAKEFLAGS="-j$(nproc)" \
    -f ${DOCKERFILE} \
    -t "${IMAGE}:${VERSION}" \
    .

# Tag as latest if build succeeds
if [ $? -eq 0 ]; then
    echo "Build successful! Tagging as latest..."
    docker tag "${IMAGE}:${VERSION}" "${IMAGE}:latest"
else
    echo "Build failed!"
    exit 1
fi
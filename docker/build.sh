#!/bin/sh

IMAGE="yasir2000/mottoagents"
VERSION=1.0

# Enable BuildKit and set configuration
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain
export BUILDKIT_CONFIG=docker/docker-buildkit.toml

# Enable debug mode for more detailed output
set -x

# Clean up any existing containers and images
docker ps -a | grep ${IMAGE} | awk '{print $1}' | xargs -r docker rm -f
docker images | grep ${IMAGE} | awk '{print $3}' | xargs -r docker rmi -f

# Build with optimizations
docker build \
  --progress=plain \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --build-arg MAKEFLAGS="-j$(nproc)" \
  --build-arg BUILDKIT_CONTEXT_KEEP_GIT_DIR=1 \
  -f docker/Dockerfile \
  -t "${IMAGE}:${VERSION}" \
  .

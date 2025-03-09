#!/bin/sh

IMAGE="yasir2000/mottoagents"
VERSION=1.0

docker build --no-cache -f Dockerfile -t "${IMAGE}:${VERSION}" .

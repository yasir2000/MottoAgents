#!/bin/bash

# Configuration
IMAGE="yasir2000/mottoagents:1.0"
CONTAINER_NAME="mottoagents"
PORT=7860
MAX_RETRIES=60

# Check Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Check if the image exists
if ! docker image inspect $IMAGE >/dev/null 2>&1; then
    echo "Error: Image $IMAGE not found"
    exit 1
fi

# Stop and remove existing container
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Start container
echo "Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --restart unless-stopped \
    $IMAGE

# Check if container started
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "Error: Container failed to start"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Wait for service
echo "Waiting for service..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s http://localhost:$PORT >/dev/null; then
        echo "Service is up at http://localhost:$PORT"
        docker logs $CONTAINER_NAME
        exit 0
    fi
    sleep 1
    echo "Attempt $i/$MAX_RETRIES..."
done

echo "Service failed to respond"
docker logs $CONTAINER_NAME
exit 1
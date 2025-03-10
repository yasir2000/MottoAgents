#!/bin/bash
set -e

IMAGE="yasir2000/mottoagents:1.0"
CONTAINER_NAME="mottoagents"
PORT=7860

# Check if the image exists
if ! docker image inspect $IMAGE >/dev/null 2>&1; then
    echo "Error: Image $IMAGE not found. Please run build.sh first."
    exit 1
fi

# Remove any existing container with the same name
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Run the container
echo "Starting MottoAgents container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --restart unless-stopped \
    $IMAGE

# Wait for container to be healthy
echo "Waiting for container to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:$PORT >/dev/null; then
        echo "Container is ready! Access the application at http://localhost:$PORT"
        docker logs -f $CONTAINER_NAME
        exit 0
    fi
    echo "Waiting for service to start... ($i/30)"
    sleep 1
done

echo "Error: Service failed to start within 30 seconds"
docker logs $CONTAINER_NAME
exit 1
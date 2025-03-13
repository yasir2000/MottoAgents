#!/bin/bash
set -eo pipefail

IMAGE="yasir2000/mottoagents"
VERSION="1.0"
PORT=7860
CONTAINER_NAME="mottoagents"

check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "Error: Docker is not running or not accessible"
        exit 1
    fi
}

cleanup_existing() {
    echo "Cleaning up existing containers..."
    if docker ps -a | grep -q ${CONTAINER_NAME}; then
        docker rm -f ${CONTAINER_NAME}
    fi
}

start_container() {
    echo "Starting container..."
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${PORT}:${PORT} \
        --restart unless-stopped \
        -v $(pwd)/logs:/var/log \
        "${IMAGE}:${VERSION}"

    # Check if container started successfully
    if ! docker ps | grep -q ${CONTAINER_NAME}; then
        echo "Error: Container failed to start. Checking logs..."
        docker logs ${CONTAINER_NAME}
        exit 1
    fi
}

wait_for_service() {
    echo "Waiting for service to be ready..."
    local max_attempts=30
    local attempt=1
    
    while ! curl -s http://localhost:${PORT} >/dev/null 2>&1; do
        if [ $attempt -gt $max_attempts ]; then
            echo "Error: Service failed to start after ${max_attempts} attempts"
            docker logs ${CONTAINER_NAME}
            exit 1
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
}

main() {
    check_docker
    cleanup_existing
    
    # Check if image exists
    if ! docker image inspect "${IMAGE}:${VERSION}" >/dev/null 2>&1; then
        echo "Image not found. Building first..."
        ./build.sh
    fi
    
    start_container
    wait_for_service
    
    echo -e "\nMottoAgents is running at http://localhost:${PORT}"
    echo "Container logs available with: docker logs ${CONTAINER_NAME}"
}

main "$@"

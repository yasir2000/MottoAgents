#!/bin/bash
set -eo pipefail

# Define project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

init_docker_files() {
    echo "Initializing docker files..."
    
    # Create docker directory if it doesn't exist
    mkdir -p "${PROJECT_ROOT}/docker"
    
    # Create required directories
    mkdir -p "${PROJECT_ROOT}/mottoagents/frontend/app"
    
    # Check if Dockerfile exists, if not copy from source
    if [ ! -f "${PROJECT_ROOT}/docker/Dockerfile" ]; then
        echo "Error: Dockerfile not found in ${PROJECT_ROOT}/docker/"
        echo "Please ensure Dockerfile exists in the docker directory"
        exit 1
    fi
    
    # Check other required files
    required_files=(
        "docker/nginx.conf"
        "docker/supervisord.conf"
        "docker/uwsgi.ini"
        "requirements.prod.txt"
        "setup.py"
        "README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "${PROJECT_ROOT}/${file}" ]; then
            echo "Error: Required file '${file}' not found"
            exit 1
        fi
    done
}

create_directories() {
    mkdir -p "${PROJECT_ROOT}/docker" "${PROJECT_ROOT}/logs"
    mkdir -p "${PROJECT_ROOT}/mottoagents/frontend/app"
}

cleanup() {
    echo "Cleaning up..."
    docker ps -aq --filter "name=mottoagents" | xargs -r docker rm -f
    docker images yasir2000/mottoagents -q | xargs -r docker rmi -f
}

build_image() {
    local log_file="${PROJECT_ROOT}/logs/build-$(date +%Y%m%d-%H%M%S).log"
    echo "Building Docker image from ${PROJECT_ROOT}/docker/Dockerfile"
    echo "Build log will be saved to: ${log_file}"
    
    cd "${PROJECT_ROOT}"
    # Add debug ls to check files
    {
        echo "=== Build Started at $(date) ==="
        echo "Current directory contents:"
        ls -la
        echo -e "\nDocker directory contents:"
        ls -la docker/
        echo -e "\nStarting Docker build...\n"
        
        docker build \
            -f docker/Dockerfile \
            -t yasir2000/mottoagents:1.0 \
            --no-cache \
            . 2>&1
            
        echo -e "\n=== Build Completed at $(date) ==="
    } | tee "${log_file}"
}

main() {
    echo "Starting build process from ${PROJECT_ROOT}"
    init_docker_files
    create_directories
    cleanup
    build_image || {
        echo "Build failed! Check build.log for details"
        exit 1
    }
}

main "$@"

#!/bin/bash

# Variables
IMAGE_NAME="fitness_tracker_api"
CONTAINER_TAG="0.1.0"
CONTAINER_NAME="${IMAGE_NAME}_container"
HOST_PORT=5000
CONTAINER_PORT=5000
BUILD=true  # Set to true if you want to build the image

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Build Docker image if required
if [ "$BUILD" = true ]; then
    echo "Building Docker image: ${IMAGE_NAME}:${CONTAINER_TAG}..."
    if ! docker build -t ${IMAGE_NAME}:${CONTAINER_TAG} .; then
        echo "Error: Failed to build the Docker image."
        exit 1
    fi
else
    echo "Skipping Docker image build..."
fi

# Stop and remove any existing container with the same name
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping existing container: ${CONTAINER_NAME}..."
    if ! docker stop ${CONTAINER_NAME}; then
        echo "Error: Failed to stop the container ${CONTAINER_NAME}."
        exit 1
    fi

    echo "Removing container: ${CONTAINER_NAME}..."
    if ! docker rm ${CONTAINER_NAME}; then
        echo "Error: Failed to remove the container ${CONTAINER_NAME}."
        exit 1
    fi
else
    echo "No existing container named ${CONTAINER_NAME} found."
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. The container may lack necessary environment variables."
fi

# Run the Docker container
echo "Starting Docker container: ${CONTAINER_NAME}..."
if docker run -d \
    --name ${CONTAINER_NAME} \
    --env-file .env \
    -p ${HOST_PORT}:${CONTAINER_PORT} \
    ${IMAGE_NAME}:${CONTAINER_TAG}; then
    echo "Docker container ${CONTAINER_NAME} is running on port ${HOST_PORT}."
else
    echo "Error: Failed to start the Docker container ${CONTAINER_NAME}."
    exit 1
fi

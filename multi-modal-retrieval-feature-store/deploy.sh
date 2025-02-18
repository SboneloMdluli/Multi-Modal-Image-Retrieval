#!/bin/bash

# Exit on any error
set -e

# Function to log messages with timestamps
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Basic checks
if ! docker info > /dev/null 2>&1; then
    log_message "Error: Docker is not running"
    exit 1
fi

for file in "feast.Dockerfile" "docker-compose.yml" "requirements.txt"; do
    if [ ! -f "$file" ]; then
        log_message "Error: $file not found"
        exit 1
    fi
done

# Setup and deploy
log_message "Setting up feature store..."
mkdir -p feature_data
cp "../multi-modal-retrieval-pipeline/data/04_feature/embeddings.pq" "feature_data/embeddings.pq"

# Clean start
log_message "Starting services..."
docker-compose down -v &>/dev/null || true
docker-compose up --build -d

# Initialize feature store
log_message "Initializing feature store..."
if ! docker-compose exec -T feast-server python initialise_store.py; then
    log_message "Error: Feature store initialization failed"
    docker-compose logs feast-server
    docker-compose down
    exit 1
fi

log_message "Deployment successful! Use 'docker-compose logs feast-server' to view logs"

#!/bin/bash

# Set environment variables
export TAG=$(date +%Y%m%d_%H%M%S)
export USER_UID=$(id -u)
export USER_GID=$(id -g)

# Create directories and set permissions
echo "Setting up directories and permissions..."
mkdir -p data/01_raw \
    data/02_intermediate \
    data/03_primary \
    data/04_feature \
    data/05_model_input \
    data/06_models \
    data/07_model_output \
    data/08_reporting \
    logs

# Set ownership and permissions (without sudo)
chmod -R 777 data \
    logs \
    conf \
    src \
    feast_repo

# Ensure feature directory is writable
touch data/04_feature/.placeholder
chmod 666 data/04_feature/.placeholder

# Build and run Kedro pipeline
echo "Starting Kedro pipeline..."
docker-compose -f docker-compose.prod.yml up --build kedro-run --abort-on-container-exit

# Check if Kedro pipeline was successful
if [ $? -ne 0 ]; then
    echo "Kedro pipeline failed. Aborting deployment."
    docker-compose -f docker-compose.prod.yml down
    exit 1
fi

# Deploy Feast features
echo "Deploying Feast features..."
docker build -t feast-deploy -f feast_repo/Dockerfile.feast .
docker run --rm \
    -v $(pwd)/data:/data \
    -v $(pwd)/feast_repo:/feast_repo \
    --user $USER_UID:$USER_GID \
    feast-deploy

/setup_dirs.sh

# Run feast commands
feast apply
feast materialize-incremental $(date -u +"%Y-%m-%d")

# Cleanup
echo "Cleaning up..."
docker-compose -f docker-compose.prod.yml down

#!/bin/bash

# Exit on any error
set -e

# Function to log messages with timestamps
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log_message "Setting up feature store..."
mkdir -p feature_data
cp "../multi-modal-retrieval-pipeline/data/04_feature/embeddings.pq" "feature_data/embeddings.pq"

# Install requirements
log_message "Installing requirements..."
pip install -r requirements.txt

# Initialize feature store
log_message "Initializing feature store..."

# Get the absolute path of the current directory
CURRENT_DIR=$(pwd)
PROJECT_ROOT=$(dirname "$CURRENT_DIR")

# Set up Python path to include the project root and current directory
export PYTHONPATH="${PROJECT_ROOT}:${CURRENT_DIR}:${PYTHONPATH:-}"

# Unset VIRTUAL_ENV to ensure we're not trying to use any virtual environment
unset VIRTUAL_ENV

# Run the initialization script (which includes feast apply)
log_message "Running initialization script..."
python3 initialise_store.py

if [ $? -eq 0 ]; then
    log_message "Feature store initialization successful!"
else
    log_message "Error: Feature store initialization failed"
    exit 1
fi

log_message "Local deployment completed successfully!"

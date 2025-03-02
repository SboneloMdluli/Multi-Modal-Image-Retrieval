#!/bin/bash

# Exit on any error
set -e

# Function to log messages with timestamps
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Get the root project directory
PROJECT_ROOT=$(dirname "$(pwd)")

# Check if virtual environment exists and activate it
if [ -f "${PROJECT_ROOT}/venv/bin/activate" ]; then
    log_message "Using project virtual environment..."
    source "${PROJECT_ROOT}/venv/bin/activate"
elif [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
    log_message "Using project virtual environment..."
    source "${PROJECT_ROOT}/.venv/bin/activate"
else
    log_message "Error: Could not find virtual environment in ${PROJECT_ROOT}"
    log_message "Please ensure you've activated the virtual environment"
    exit 1
fi

log_message "Using Python from: $(which python)"

# Create necessary directories
log_message "Setting up feature store..."
mkdir -p feature_data
cp "../multi-modal-retrieval-pipeline/data/04_feature/embeddings.pq" "feature_data/embeddings.pq"

# Install requirements
log_message "Installing requirements..."
python -m pip install --upgrade pip

pip install -r requirements.txt

# Initialize feature store
log_message "Initialising feature store..."

# Get the absolute path of the current directory
CURRENT_DIR=$(pwd)
PROJECT_ROOT=$(dirname "$CURRENT_DIR")

# Set up Python path to include the project root and current directory
export PYTHONPATH="${PROJECT_ROOT}:${CURRENT_DIR}:${PYTHONPATH:-}"

log_message "Running initialisation script..."
python initialise_store.py

if [ $? -eq 0 ]; then
    log_message "Feature store initialisation successful!"
else
    log_message "Error: Feature store initialisation failed"
    exit 1
fi

log_message "Local deployment completed successfully!"

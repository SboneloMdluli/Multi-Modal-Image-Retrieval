#!/bin/bash

# Exit on any error
set -e

# Function to log messages with timestamps
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Create necessary directories
log_message "Creating directories..."
mkdir -p logs

# Install main project requirements
log_message "Installing main project requirements..."
pip install -r requirements.txt

# Run Kedro pipeline
log_message "Running Kedro pipeline..."
kedro run --async

# Check if Kedro pipeline was successful
if [ $? -eq 0 ]; then
    log_message "Kedro pipeline completed successfully"
else
    log_message "Error: Kedro pipeline failed"
    exit 1
fi

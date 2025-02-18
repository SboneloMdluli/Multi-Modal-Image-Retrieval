#!/bin/bash

# Function to log messages with timestamps
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Create necessary directories
log_message "Creating data directory..."
mkdir -p data/online_store
mkdir -p data/registry
mkdir -p data/feature_repo

log_message "Creating logs directory..."
mkdir -p logs

# Set permissions
log_message "Setting permissions..."
chmod -R 777 data
chmod -R 777 logs

log_message "Directory structure created successfully"

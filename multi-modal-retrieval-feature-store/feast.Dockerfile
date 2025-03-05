FROM python:3.11-slim

WORKDIR /feast_feature_store

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Set up environment
ENV PYTHONPATH=/feast_feature_store

# Default command
CMD ["python", "initialise_store.py"]

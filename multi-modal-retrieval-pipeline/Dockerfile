# Build stage
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy the entire project for installation
COPY . .

# Install dependencies and the project itself
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Final stage
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    USER_NAME=kedro \
    USER_UID=1000 \
    USER_GID=1000 \
    PATH="/home/kedro/.local/bin:${PATH}" \
    HF_HOME="/home/kedro/.cache/huggingface"

RUN groupadd --gid $USER_GID $USER_NAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the entire project
COPY --chown=$USER_NAME:$USER_NAME . .

# Create directories with proper permissions
RUN mkdir -p /app/data/01_raw \
    /app/data/02_intermediate \
    /app/data/03_primary \
    /app/data/04_feature \
    /app/data/05_model_input \
    /app/data/06_models \
    /app/data/07_model_output \
    /app/data/08_reporting \
    /app/logs \
    /home/kedro/logs \
    /home/kedro/.cache/huggingface/hub \
    && chown -R $USER_NAME:$USER_NAME /app \
    && chown -R $USER_NAME:$USER_NAME /home/kedro/logs \
    && chown -R $USER_NAME:$USER_NAME /home/kedro/.cache \
    && chmod -R 777 /home/kedro/.cache/huggingface

USER $USER_NAME

# Verify kedro installation
RUN kedro --version

CMD ["kedro", "run", "--async"]

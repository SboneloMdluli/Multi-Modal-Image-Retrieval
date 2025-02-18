#!/bin/bash

# Stop containers
docker-compose -f docker-compose.prod.yml down

# Remove old volumes (optional, uncomment if needed)
# docker volume prune -f

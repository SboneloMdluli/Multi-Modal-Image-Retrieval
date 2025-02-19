#!/bin/bash

echo "🔄 Building and starting Docker containers..."
docker-compose up -d

echo "\n📊 Container Status:"
docker-compose ps

echo "\n📝 Container Logs:"
docker-compose logs -f

#!/bin/bash
set -e

# Load environment variables
source .env

# Build Docker images
echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml build

# Push Docker images to registry (if using a registry)
# echo "Pushing Docker images to registry..."
# docker-compose -f docker-compose.prod.yml push

# Deploy to production
echo "Deploying to production..."
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations (if using a database)
# echo "Running database migrations..."
# docker-compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head

# Health check
echo "Performing health check..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment completed successfully!" 
#!/bin/bash

# Notion to Word Converter - Quick Start Script
# This script helps you quickly deploy the application using Docker

set -e

echo "🚀 Notion to Word Converter - Docker Deployment"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Generate secret key if .env doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file with secure secret key..."
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))' 2>/dev/null || openssl rand -hex 32)
    cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
PORT=5000
MAX_CONTENT_LENGTH=104857600
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads output
chmod 755 uploads output
echo "✅ Directories created"

# Build and start the container
echo ""
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting container..."
docker-compose up -d

# Wait for the application to start
echo ""
echo "⏳ Waiting for application to start..."
sleep 5

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Application is running!"
    echo ""
    echo "🌐 Access the application at: http://localhost:5000"
    echo ""
    echo "📊 View logs: docker-compose logs -f"
    echo "🛑 Stop application: docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Error: Container failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

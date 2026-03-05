#!/bin/bash
# Startup script for Movie Ratings App

set -e

echo "🎬 Movie Ratings Spreadsheet - Setup"
echo "======================================"

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

# Check if Excel file exists
if [ ! -f "data/Movie Ratings.xlsx" ]; then
    echo ""
    echo "⚠️  Excel file not found!"
    echo "Please copy your 'Movie Ratings.xlsx' file to the 'data/' directory"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  OMDB API key not configured!"
    echo "To enable movie poster fetching:"
    echo "1. Get a free API key from: http://www.omdbapi.com/apikey.aspx"
    echo "2. Edit .env file and add your key"
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo ""
echo "🚀 Starting Movie Ratings App..."
echo ""

# Build and start containers
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Application is running!"
    echo ""
    echo "🌐 Access the app at: http://localhost:5000"
    echo ""
    echo "📋 Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop app: docker-compose down"
    echo "  - Restart: docker-compose restart"
    echo "  - Fetch posters: docker-compose exec web python /app/fetch_posters.py"
    echo ""
else
    echo "❌ Something went wrong. Check logs with: docker-compose logs"
    exit 1
fi

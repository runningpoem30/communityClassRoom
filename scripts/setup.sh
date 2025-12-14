#!/bin/bash

# ========================================
# AutoMaintainer AI - Setup Script
# ========================================

set -e

echo "🚀 Setting up AutoMaintainer AI..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install Node.js and npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Set up environment variables
echo "🔧 Setting up environment variables..."

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys before continuing"
    echo "   Required: ANTHROPIC_API_KEY, GITHUB_TOKEN, DATABASE_URL"
    read -p "Press Enter after you've configured .env..."
else
    echo "✅ .env file already exists"
fi

# Start PostgreSQL and Kestra
echo "🐳 Starting Docker services (PostgreSQL + Kestra)..."
docker-compose up -d

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if database is ready
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "  Waiting for database..."
    sleep 2
done

echo "✅ PostgreSQL is ready"

# Initialize database schema
echo "📊 Initializing database schema..."
docker-compose exec -T postgres psql -U postgres -d automaintainer -f /docker-entrypoint-initdb.d/01-schema.sql || echo "Schema already exists"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

# Return to root
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Start the frontend: cd frontend && npm run dev"
echo "   2. Access Kestra UI: http://localhost:8080"
echo "   3. Upload workflow: workflows/main-orchestration.yml to Kestra"
echo "   4. Access Dashboard: http://localhost:3000"
echo ""
echo "🎯 To run a complete agent cycle:"
echo "   - Trigger the workflow in Kestra UI"
echo "   - Monitor progress in Kestra"
echo "   - View results in dashboard at http://localhost:3000"
echo ""

#!/bin/bash
set -e

echo "🚀 Bootstrapping Market Intel Platform Development Environment"

# Check prerequisites
echo "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "✅ Poetry installed"
fi

echo "✅ All prerequisites met"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update with your actual credentials."
else
    echo "✅ .env file already exists"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
poetry install
cd ..
echo "✅ Backend dependencies installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✅ Frontend dependencies installed"

# Start infrastructure services
echo "🐳 Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Run database migrations
echo "🗃️  Running database migrations..."
cd backend
poetry run alembic upgrade head
cd ..
echo "✅ Database migrations completed"

# Create some sample data (optional)
echo "📊 Would you like to create sample market data? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Creating sample data..."
    cd backend
    poetry run python -c "
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.database.connection import SessionLocal
from app.models.database import MarketBar

# Create sample data
symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT']
db = SessionLocal()

for symbol in symbols:
    start_date = datetime.utcnow() - timedelta(days=90)
    for i in range(90):
        date = start_date + timedelta(days=i)
        price = 100 + np.random.uniform(-5, 5)
        
        bar = MarketBar(
            symbol=symbol,
            timestamp=date,
            timeframe='1d',
            open=price,
            high=price * 1.02,
            low=price * 0.98,
            close=price * (1 + np.random.uniform(-0.02, 0.02)),
            volume=1000000 + np.random.uniform(0, 500000)
        )
        db.add(bar)

db.commit()
db.close()
print('Sample data created successfully')
"
    cd ..
    echo "✅ Sample data created"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update .env file with your API keys"
echo "2. Start the services:"
echo "   - Backend API: make api"
echo "   - Frontend: make frontend"
echo "   - All services: make up"
echo ""
echo "Useful commands:"
echo "   - make help           # Show all available commands"
echo "   - make up             # Start all services"
echo "   - make logs           # View service logs"
echo "   - make tests          # Run tests"
echo "   - make lint           # Run code quality checks"
echo ""
echo "URLs:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"
echo "   - Airflow: http://localhost:8080 (admin/admin)"
echo ""
echo "Happy coding! 🚀"
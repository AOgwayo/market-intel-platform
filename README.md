# Market Intelligence Platform

A comprehensive market intelligence and algorithmic trading platform built with modern technologies for real-time market analysis, strategy development, and automated trading.

## 🚀 Features

- **Real-time Market Data Ingestion**: WebSocket connections to major exchanges
- **Advanced Strategy Engine**: Multiple algorithmic trading strategies with backtesting
- **Risk Management**: Comprehensive risk checks and position management  
- **Modern Web Interface**: React/Next.js frontend with real-time updates
- **Scalable Architecture**: Microservices with Docker containerization
- **Data Pipeline**: Automated ETL workflows with Apache Airflow
- **API-First Design**: RESTful API with comprehensive documentation

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** for high-performance API development
- **SQLAlchemy** for database ORM with PostgreSQL
- **Alembic** for database migrations
- **Redis** for caching and session management
- **Apache Airflow** for data pipeline orchestration

### Frontend (Next.js/React)
- **Next.js 14** with App Router
- **Chakra UI** for modern, accessible components
- **TypeScript** for type safety
- **SWR** for data fetching and caching

### Infrastructure
- **Docker Compose** for development environment
- **PostgreSQL** for primary data storage
- **Redis** for caching and real-time features
- **Nginx** for reverse proxy (production)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- Poetry (Python package manager)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd market-intel-platform
   ```

2. **Bootstrap development environment**
   ```bash
   ./scripts/dev_bootstrap.sh
   ```

3. **Start services**
   ```bash
   # Start all services
   make up
   
   # Or start individually
   make api      # Backend API
   make frontend # Frontend dev server
   ```

4. **Access the applications**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Airflow: http://localhost:8080 (admin/admin)

### Manual Setup (Alternative)

1. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install Dependencies**
   ```bash
   make install
   ```

3. **Start Infrastructure**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run Database Migrations**
   ```bash
   make migrate
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1: Backend API
   make api
   
   # Terminal 2: Frontend
   make frontend
   ```

## 📊 Trading Strategies

The platform includes several built-in algorithmic trading strategies:

- **Mean Reversion** (`mean_reversion_v1`): Bollinger Bands-based strategy
- **Momentum** (`momentum_v1`): RSI-based momentum trading (stub)
- **Volatility Breakout** (`vol_breakout_v1`): Volatility breakout strategy (stub) 
- **Regime Detection** (`regime_detection_v1`): Market regime detection (stub)

### Strategy Development
```python
from app.strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signal(self, symbol, bars, current_price):
        # Your strategy logic here
        return signal
```

## 🔧 Development

### Available Commands
```bash
make help           # Show all available commands
make install        # Install all dependencies
make up            # Start all services
make down          # Stop all services  
make tests         # Run tests
make lint          # Run linting
make format        # Format code
make migrate       # Run database migrations
make generate-types # Generate TypeScript types
```

### Code Quality
- **Linting**: Ruff for Python, ESLint for TypeScript
- **Formatting**: Black for Python, Prettier for TypeScript
- **Type Checking**: MyPy for Python, TypeScript compiler
- **Testing**: Pytest for Python, Jest for TypeScript

### Database Migrations
```bash
# Create new migration
make migrate-create MESSAGE="Add new table"

# Apply migrations
make migrate

# Rollback migration
make migrate-down
```

## 📈 API Endpoints

### Market Data
- `GET /v1/market/bars/{symbol}` - Get market bars
- `GET /v1/market/symbols` - List available symbols

### Signals
- `GET /v1/signals/{symbol}/latest` - Get latest signal
- `GET /v1/signals/` - List signals with filters

### Trading
- `POST /v1/trading/orders` - Place order
- `DELETE /v1/trading/orders/{order_id}` - Cancel order
- `GET /v1/trading/positions` - Get positions

### Backtesting
- `POST /v1/backtest/mean_reversion` - Run mean reversion backtest

### Models
- `GET /v1/models/strategies` - List available strategies
- `GET /v1/models/strategies/{name}` - Get strategy details

## 🔒 Security & Environment Variables

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/market_intel

# Trading APIs
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key

# Security
SECRET_KEY=your-secret-key-here

# External APIs
BINANCE_API_KEY=your-binance-api-key
```

**⚠️ Important Security Notes:**
- Never commit real API keys to version control
- Use paper trading accounts for development
- Rotate API keys regularly
- Use strong, unique secret keys in production

## 🧪 Testing

```bash
# Run all tests
make tests

# Run specific test categories
make test-api
make test-strategies

# Run with coverage
cd backend && poetry run pytest --cov=app
```

## 📋 Data Pipeline

Apache Airflow DAGs handle:
- **Daily Bars Pipeline**: Daily market data ingestion
- **Intraday Ingestion**: Real-time data processing  
- **Model Training**: ML model training and deployment

Access Airflow UI at http://localhost:8080 (admin/admin)

## 🚨 Monitoring & Health

- Health check: `GET /health`
- Service status: `make status`  
- Logs: `make logs`
- Health check all services: `make health-check`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Development Guidelines
- Follow existing code style
- Write tests for new features
- Update documentation
- Use semantic commit messages

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [Data Model](docs/data-model.md)
- [ADR-0001: Technology Stack](docs/adr/ADR-0001-tech-stack.md)

## ⚖️ Legal Disclaimers

**IMPORTANT DISCLAIMERS:**

- **Not Financial Advice**: This platform is for educational and research purposes only
- **Trading Risks**: Algorithmic trading involves substantial risk of loss
- **No Warranty**: Software provided "as-is" without warranties
- **Compliance**: Users responsible for regulatory compliance
- **Paper Trading**: Use paper trading accounts for development and testing

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Documentation: Check the `docs/` directory
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## 🎯 Roadmap

- [ ] Advanced ML models for market prediction
- [ ] Multi-broker support (Interactive Brokers, TD Ameritrade)
- [ ] Real-time portfolio optimization
- [ ] Advanced risk management features
- [ ] Mobile application
- [ ] Cloud deployment guides
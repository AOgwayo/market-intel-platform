# Market Intelligence Platform

Real-time market intelligence platform with data ingestion from Polygon.io (equities) and Binance (crypto), automated strategy execution, and comprehensive market analysis capabilities.

## Features

- **Real-time Data Ingestion**
  - Polygon.io integration for equity minute bars and daily aggregates
  - Binance WebSocket streaming for crypto trade data with 1-minute bar aggregation
  - Automated incremental data updates via Airflow

- **Data Storage & Management**
  - PostgreSQL database with optimized market data schema
  - Conflict handling for partial bar re-aggregation
  - Efficient upsert operations with timestamp-based deduplication

- **Strategy Framework**
  - Pluggable strategy runner architecture
  - Built-in mean reversion strategy (v1)
  - Near real-time signal generation on new data

- **Infrastructure**
  - Docker Compose for easy deployment
  - Apache Airflow for scheduling and orchestration
  - FastAPI web service for data access
  - Comprehensive logging and error handling

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Polygon.io API key (for equity data)

### Setup

1. **Clone and configure environment**:
   ```bash
   git clone <repository-url>
   cd market-intel-platform
   cp .env.example .env
   ```

2. **Add your Polygon API key** to `.env`:
   ```bash
   POLYGON_API_KEY=your_polygon_api_key_here
   ```

3. **Start the platform**:
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**:
   - Web API: http://localhost:8000
   - Airflow: http://localhost:8080
   - Database: localhost:5432

### Data Ingestion

#### Polygon Equity Data

The system automatically ingests equity data via the Airflow DAG `polygon_equities_minute_ingest`:

- **Schedule**: Every 15 minutes (`*/15 * * * *`)
- **Symbols**: Configurable via `INGEST_EQUITY_SYMBOLS` (default: AAPL,MSFT,TSLA,GOOGL,AMZN)
- **Data**: Historical minute bars with incremental updates
- **Conflict Handling**: Automatic upsert with OHLCV updates for partial bars

#### Binance Crypto Streaming

Run the Binance trade stream manually for real-time crypto data:

```bash
# Stream BTCUSDT (default)
python -m backend.app.ingestion.binance_stream

# Stream specific symbol
python -m backend.app.ingestion.binance_stream --symbol ETHUSDT
```

Features:
- Real-time trade stream aggregation to 1-minute bars
- Automatic reconnection and error handling
- Periodic database flushes (every 60 seconds)

### API Usage

#### Get Recent Bars
```bash
curl http://localhost:8000/bars/AAPL?limit=10
```

#### List Available Symbols
```bash
curl http://localhost:8000/symbols
```

#### Health Check
```bash
curl http://localhost:8000/health
```

### Strategy Execution

The platform includes a basic strategy runner that can be triggered after data ingestion:

```python
from backend.app.strategies.runner import run_strategies_for_symbols

# Run strategies for configured symbols
results = run_strategies_for_symbols(['AAPL', 'MSFT'])
```

## Configuration

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/market_intel

# API Keys
POLYGON_API_KEY=your_polygon_api_key_here

# Ingestion
INGEST_EQUITY_SYMBOLS=AAPL,MSFT,TSLA,GOOGL,AMZN

# Binance
BINANCE_DEFAULT_SYMBOL=BTCUSDT

# Application
DEBUG=false
LOG_LEVEL=INFO
```

## Development

### Running Tests

```bash
# Install dependencies
pip install -e .

# Run tests
pytest tests/

# Run specific test
pytest tests/test_polygon_normalize.py -v
```

### Adding New Strategies

1. Create strategy in `backend/app/strategies/`
2. Register in `runner.py`
3. Update Airflow DAG to trigger on new data (optional)

### Manual Data Ingestion

```python
import asyncio
from backend.app.ingestion.polygon_equities import ingest_historical_minute_bars

# Ingest specific symbol range
asyncio.run(ingest_historical_minute_bars(['AAPL'], start_date, end_date))
```

## Architecture

```
├── backend/app/
│   ├── core/           # Configuration and settings
│   ├── models/         # Database models and schemas
│   ├── ingestion/      # Data ingestion modules
│   │   ├── polygon_equities.py    # Polygon.io integration
│   │   ├── binance_stream.py      # Binance WebSocket client
│   │   └── bar_writer.py          # Database writer utility
│   ├── strategies/     # Trading strategy framework
│   └── main.py         # FastAPI application
├── airflow/dags/       # Airflow workflow definitions
├── tests/              # Test suite
└── docs/               # Documentation
```

## Monitoring

- **Airflow UI**: Monitor DAG execution, view logs, and manage schedules
- **Application Logs**: Structured logging with configurable levels
- **Health Endpoints**: Built-in health checks for all services
- **Database Metrics**: Query performance and data quality monitoring

## Troubleshooting

### Common Issues

1. **DAG not appearing in Airflow**:
   - Check Airflow logs for parsing errors
   - Ensure backend module is in Python path

2. **Polygon API rate limits**:
   - Built-in exponential backoff retry logic
   - Check API key tier limits

3. **WebSocket disconnections**:
   - Automatic reconnection with exponential backoff
   - Monitor logs for connection status

4. **Database connection issues**:
   - Verify PostgreSQL container is running
   - Check database credentials in `.env`

For more detailed information, see [docs/ingestion.md](docs/ingestion.md).
# Market Intelligence Platform

A robust, scalable platform for ingesting, processing, and analyzing financial market data with built-in reliability, observability, and operational excellence.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   External      │    │   Ingestion      │    │   Database      │
│   Data Sources  │───▶│   Pipeline       │───▶│   (PostgreSQL)  │
│                 │    │                  │    │                 │
│ • REST APIs     │    │ • Retry Logic    │    │ • Time Series   │
│ • WebSockets    │    │ • Rate Limiting  │    │ • Bars Table    │
│ • Market Feeds  │    │ • Error Handling │    │ • Unique Index  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Structured     │
                       │   Logging        │
                       │                  │
                       │ • JSON Format    │
                       │ • Context Rich   │
                       │ • Searchable     │
                       └──────────────────┘
```

## Features

- **Structured Logging**: JSON-formatted logs with rich context using structlog
- **Configuration Management**: Environment-based config with validation and fail-fast behavior  
- **Retry Logic**: Exponential backoff with jitter for resilient data ingestion
- **Database Migrations**: Schema evolution with idempotent upsert patterns
- **Code Quality**: Pre-commit hooks with black, ruff, mypy, and isort
- **Operational Excellence**: Comprehensive logging, error handling, and monitoring hooks

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AOgwayo/market-intel-platform.git
   cd market-intel-platform
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env  # Create from example (if exists)
   # Edit .env with your configuration (see Environment Variables section)
   ```

5. **Set up pre-commit hooks (optional but recommended)**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Run database migrations**
   ```bash
   # Apply the unique index migration to your database
   psql -d your_database -f migrations/20250901_add_bars_unique_index.sql
   ```

7. **Run the ingestion loop**
   ```bash
   python -m src.ingestion.ingest_loop
   ```

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `APP_ENV` | `development` | No | Application environment (development/staging/production) |
| `LOG_LEVEL` | `INFO` | No | Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `DB_DSN` | - | **Yes** | Database connection string (e.g., `postgresql://user:pass@host:port/db`) |
| `INGEST_POLL_INTERVAL_SECONDS` | `60` | No | Seconds between ingestion cycles (must be > 0) |
| `INGEST_BATCH_SIZE` | `500` | No | Number of bars to process per batch (must be > 0) |
| `RETRY_MAX_ATTEMPTS` | `5` | No | Maximum retry attempts for failed operations (must be > 0) |
| `RETRY_BASE_DELAY` | `0.5` | No | Base delay in seconds for exponential backoff (must be > 0) |
| `RETRY_MAX_DELAY` | `30.0` | No | Maximum delay cap in seconds (must be >= base delay) |
| `BARS_TIMEFRAME_DEFAULT` | - | No | Default timeframe for bar data (e.g., '1m', '5m', '1h') |

### Example .env file

```bash
APP_ENV=development
LOG_LEVEL=INFO
DB_DSN=postgresql://username:password@localhost:5432/market_intel
INGEST_POLL_INTERVAL_SECONDS=60
INGEST_BATCH_SIZE=500
RETRY_MAX_ATTEMPTS=5
RETRY_BASE_DELAY=0.5
RETRY_MAX_DELAY=30.0
BARS_TIMEFRAME_DEFAULT=1m
```

## Project Structure

```
market-intel-platform/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration schema & validation
│   ├── logging_setup.py          # Structured logging configuration
│   ├── retry.py                  # Exponential backoff retry utility
│   └── ingestion/
│       ├── __init__.py
│       └── ingest_loop.py        # Main ingestion pipeline
├── migrations/
│   └── 20250901_add_bars_unique_index.sql  # Database schema migration
├── .pre-commit-config.yaml       # Code quality hooks
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Development Workflow

### Code Quality

The project uses pre-commit hooks to maintain code quality:

- **black**: Code formatting with 100-character line length
- **isort**: Import sorting compatible with black
- **ruff**: Fast Python linter with auto-fixes
- **mypy**: Static type checking
- **Standard hooks**: Trailing whitespace, YAML validation, etc.

### Running Quality Checks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
pre-commit run mypy
```

### Adding New Components

1. Follow the existing module structure under `src/`
2. Use structured logging with component-specific loggers
3. Integrate configuration through the central `Config` class
4. Apply retry logic for external dependencies
5. Add appropriate error handling and validation
6. Update environment variable documentation

## Database Schema

### Bars Table Structure (Example)

```sql
CREATE TABLE bars (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    ts BIGINT NOT NULL,
    open DECIMAL(15,8) NOT NULL,
    high DECIMAL(15,8) NOT NULL,
    low DECIMAL(15,8) NOT NULL,
    close DECIMAL(15,8) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Unique index for idempotent upserts
CREATE UNIQUE INDEX idx_bars_symbol_timeframe_ts_unique 
ON bars (symbol, timeframe, ts);
```

### Idempotent Upsert Pattern

```sql
INSERT INTO bars (symbol, timeframe, ts, open, high, low, close, volume, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
ON CONFLICT (symbol, timeframe, ts)
DO UPDATE SET
  open = EXCLUDED.open,
  high = EXCLUDED.high,
  low = EXCLUDED.low,
  close = EXCLUDED.close,
  volume = EXCLUDED.volume,
  updated_at = NOW();
```

## Operational Guidance

### Logging

All logs are structured JSON with consistent fields:

- `timestamp`: UTC ISO8601 timestamp
- `level`: Log level (INFO, WARNING, ERROR, etc.)
- `env`: Application environment
- `component`: Source component (ingestion, config, retry, etc.)
- `event`: Specific event name for filtering and alerting

### Key Log Events

- `service_start` / `service_stop`: Service lifecycle
- `config_loaded` / `config_error`: Configuration events
- `retry_attempt_fetch` / `retry_backoff_fetch`: Retry logic
- `ingest_batch_success` / `ingest_batch_failed`: Batch processing
- `db_operation_start` / `db_operation_success`: Database operations

### Monitoring & Alerting

Monitor these log events for operational health:

- **Critical**: `config_error`, `ingest_cycle_failed`, `service_stop` with error
- **Warning**: `retry_backoff_fetch`, `ingest_batch_failed`
- **Info**: `service_start`, `ingest_batch_success`

### Error Handling

The platform implements layered error handling:

1. **Configuration Errors**: Fail fast on startup with clear messages
2. **Retryable Errors**: Exponential backoff for transient failures
3. **Non-retryable Errors**: Immediate failure for permanent issues
4. **Structured Logging**: Rich context for debugging and monitoring

## Future Roadmap

- [ ] Implement actual external API integrations
- [ ] Add database connection pooling and transaction management
- [ ] Integrate metrics collection (Prometheus/StatsD)
- [ ] Add correlation ID propagation for request tracing
- [ ] Implement dead-letter queue for failed messages
- [ ] Add comprehensive test suite
- [ ] Container deployment with Docker/Kubernetes
- [ ] API endpoints for data retrieval and health checks

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following the code quality standards
4. Run pre-commit hooks (`pre-commit run --all-files`)
5. Commit changes with descriptive messages
6. Push to your branch and create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
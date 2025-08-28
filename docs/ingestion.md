# Data Ingestion Documentation

This document provides detailed information about the data ingestion flows, rate limits, and future improvements for the Market Intelligence Platform.

## Overview

The platform supports two primary data sources:
1. **Polygon.io** - Historical and real-time equity data
2. **Binance** - Real-time cryptocurrency data via WebSocket streaming

## Polygon.io Integration

### Authentication
- Requires valid Polygon.io API key
- Set `POLYGON_API_KEY` in environment variables
- Free tier allows 5 requests per minute

### Data Types

#### Historical Minute Bars
- **Endpoint**: `/v2/aggs/ticker/{symbol}/range/1/minute/{from}/{to}`
- **Purpose**: Backfill and incremental updates
- **Frequency**: Every 15 minutes via Airflow DAG
- **Retention**: All historical data since configured start date

#### Daily Aggregates
- **Endpoint**: `/v2/aggs/ticker/{symbol}/prev`
- **Purpose**: Previous day's OHLCV data
- **Use Case**: Gap filling and daily strategy signals

### Rate Limits
- **Free Tier**: 5 requests per minute, 1000 per month
- **Starter ($200/month)**: 100 requests per minute
- **Developer ($395/month)**: 1000 requests per minute

### Error Handling
- Exponential backoff for rate limits (respects `Retry-After` header)
- Automatic retry up to 3 times
- Graceful degradation when API key missing

### Data Normalization

Polygon responses are normalized to internal format:

```python
{
    "symbol": "AAPL",
    "timestamp": datetime(2024, 1, 1, 9, 30),
    "timeframe": "1m",
    "open": 150.25,
    "high": 150.75,
    "low": 150.00,
    "close": 150.50,
    "volume": 1500000,
    "num_trades": 1250,
    "source": "polygon"
}
```

## Binance Integration

### WebSocket Connection
- **URL**: `wss://stream.binance.com:9443/ws/{symbol}@trade`
- **Default Symbol**: BTCUSDT
- **Data Type**: Individual trade executions

### Real-time Aggregation
- Aggregates trades into 1-minute OHLCV bars
- Handles minute boundary crossings automatically
- Maintains in-memory state for current bar

### Features
- **Auto-reconnection**: Exponential backoff on connection failures
- **Data Integrity**: Complete bars only (no partial data)
- **Performance**: Minimal memory footprint with periodic DB flushes
- **Flexibility**: Configurable flush intervals and symbols

### Sample Trade Data
```json
{
    "e": "trade",
    "E": 1640995200000,
    "s": "BTCUSDT",
    "t": 12345,
    "p": "46000.00",
    "q": "0.001",
    "T": 1640995200000
}
```

## Database Schema

### MarketBar Table
```sql
CREATE TABLE market_bars (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    timeframe VARCHAR DEFAULT '1m',
    open_price FLOAT NOT NULL,
    high_price FLOAT NOT NULL,
    low_price FLOAT NOT NULL,
    close_price FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    num_trades INTEGER,
    source VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, timestamp)
);

CREATE INDEX idx_symbol_timeframe_timestamp ON market_bars(symbol, timeframe, timestamp);
```

### Conflict Resolution
- **Primary Constraint**: `(symbol, timestamp)` unique index
- **Upsert Strategy**: PostgreSQL `ON CONFLICT DO UPDATE`
- **Update Fields**: OHLCV data, num_trades, updated_at
- **Use Case**: Partial bar re-aggregation and late-arriving data

## Airflow DAG Configuration

### polygon_equities_minute_ingest
- **Schedule**: `*/15 * * * *` (every 15 minutes)
- **Execution**: Incremental ingestion from last known timestamp
- **Parallelization**: One symbol per task (configurable)
- **Error Handling**: Individual symbol failures don't affect others
- **Strategy Trigger**: Optional post-ingestion strategy execution

### Task Flow
1. **check_polygon_api_key**: Validate API key configuration
2. **ingest_polygon_minute_data**: Main ingestion logic
3. **trigger_strategy_run**: Optional strategy execution

## Performance Considerations

### Database Optimizations
- **Indexes**: Optimized for time-series queries
- **Partitioning**: Consider partitioning by date for large datasets
- **Connection Pooling**: SQLAlchemy connection management
- **Batch Operations**: Bulk upserts for efficiency

### Memory Management
- **Streaming**: Process data in chunks to avoid memory spikes
- **Connection Limits**: Proper session management and cleanup
- **Binance Aggregator**: Minimal memory footprint with periodic flushes

### Network Optimization
- **Async Operations**: Non-blocking HTTP requests
- **Connection Reuse**: aiohttp session management
- **Compression**: Enable gzip for HTTP responses

## Future Improvements

### Data Quality
- **Corporate Actions**: Adjust historical prices for splits/dividends
- **Gap Detection**: Identify and fill missing data periods
- **Data Validation**: Price/volume sanity checks
- **Duplicate Detection**: Enhanced deduplication logic

### Performance Enhancements
- **Caching Layer**: Redis for frequently accessed data
- **Data Compression**: Optimize storage for historical data
- **Parallel Processing**: Multi-threaded ingestion for large symbol sets
- **Real-time Streaming**: Kafka integration for low-latency feeds

### Monitoring & Observability
- **Metrics Collection**: Prometheus/Grafana integration
- **Data Lineage**: Track data sources and transformations
- **Alert System**: Notify on ingestion failures or delays
- **Performance Dashboards**: Monitor ingestion rates and latencies

### Additional Data Sources
- **Alpha Vantage**: Alternative equity data provider
- **IEX Cloud**: Real-time and historical market data
- **Quandl**: Economic and financial datasets
- **Yahoo Finance**: Free alternative data source

### Advanced Features
- **Real-time Options Data**: Extend to derivatives markets
- **News Integration**: Sentiment analysis and event correlation
- **Alternative Data**: Social media, satellite imagery, etc.
- **Multi-Exchange Support**: Cross-venue data normalization

## Troubleshooting

### Common Issues

1. **API Rate Limits**
   - Monitor request frequency
   - Implement circuit breakers
   - Consider upgrading API tier

2. **WebSocket Disconnections**
   - Check network stability
   - Review connection logs
   - Adjust reconnection parameters

3. **Data Gaps**
   - Verify market hours and holidays
   - Check symbol validity
   - Review API response status

4. **Performance Issues**
   - Monitor database query performance
   - Check system resources
   - Review ingestion batch sizes

### Debugging Tools
- **Airflow Logs**: Detailed execution logs in Airflow UI
- **Application Logs**: Structured logging with correlation IDs
- **Database Queries**: Monitor slow queries and index usage
- **Network Tools**: Wireshark for WebSocket debugging

## Configuration Examples

### High-Frequency Setup
```bash
# Aggressive ingestion for active trading
INGEST_EQUITY_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,SPY,QQQ
POLYGON_API_KEY=your_paid_tier_key
BINANCE_DEFAULT_SYMBOL=BTCUSDT

# Airflow: Schedule every 5 minutes
# Database: Enable connection pooling
```

### Conservative Setup
```bash
# Minimal resource usage
INGEST_EQUITY_SYMBOLS=SPY,QQQ
POLYGON_API_KEY=your_free_tier_key

# Airflow: Schedule every hour
# Database: Single connection mode
```

## API Reference

### Internal Functions

#### `ingest_historical_minute_bars(symbols, start_date, end_date)`
Async function for batch ingestion of historical data.

#### `run_binance_stream(symbol, duration)`
Start WebSocket stream for specified symbol and duration.

#### `write_bars_to_db(bars, source)`
Utility function for database operations with conflict handling.

For implementation details, see the respective module documentation.
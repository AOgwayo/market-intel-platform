# Data Pipeline

1. Fetch raw bars/trades from provider
2. Validate (schema, nulls, ranges)
3. Normalize (symbol canonicalization, timestamps -> UTC)
4. Persist (raw -> curated)
5. Serve via API & streaming

## Symbol Normalization
- Equities: TICKER
- Crypto: BINANCE:BTCUSDT -> BTCUSDT canonical

## Future
- Corporate actions adjustments (splits/dividends)
# Market Intel Platform

A unified platform for ingesting, normalizing, and serving real-time and historical market data across:
- Equities (Polygon.io)
- Crypto (Binance)
- (Planned) Additional sources (news, alternative data, sentiment)

## 1. Vision
Provide a modular, extensible data & analytics layer enabling:
- Pluggable ingestion adapters
- Schema normalization
- Efficient time-series storage
- Programmatic & realtime access (API + WebSocket)
- Backtesting, signal research & dashboards

## 2. Architecture (Planned)
```
               +---------------------+
               |   External Sources  |
        +------+---------+-----------+------+
        |                |                  |
   Polygon (Equities)  Binance (Crypto)   (More)
        |                |                  |
        v                v                  v
   Ingestion Adapters (async tasks / schedulers)
        |  parse / validate / enrich
        v
   Normalization Layer (unified symbols, asset metadata)
        |
        v
   Storage Layer
     - Relational (metadata/config)
     - Time-Series (bars, trades)
        |
        v
   API & Streaming Services
        - REST / GraphQL
        - WebSocket (live stream fanout)
        |
        v
   Consumers
     - Notebooks / Analytics
     - Backtesting Engine
     - Dashboards (frontend)
```

## 3. Repo Structure (Initial)
```
backend/
  pyproject.toml
  src/market_intel/
    __init__.py
    config.py
    logging_config.py
    models/
      __init__.py
      bar.py
      trade.py
      symbol.py
    ingestion/
      __init__.py
      base.py
      polygon_adapter.py
      binance_adapter.py
      scheduler.py
    normalization/
      __init__.py
      normalizer.py
    storage/
      __init__.py
      interface.py
      memory_store.py
    api/
      __init__.py
      main.py
tests/
  test_health.py
frontend/
  package.json
  vite.config.js
  src/
    main.tsx
    App.tsx
.github/workflows/
  ci.yml
docs/
  architecture.md
  data-pipeline.md
docker/
  docker-compose.yml
.gitignore
LICENSE (placeholder)
```

## 4. Technology Stack (Initial)
| Layer        | Choice (initial)            |
|--------------|-----------------------------|
| Backend API  | FastAPI                     |
| HTTP client  | httpx (async)               |
| Scheduling   | APScheduler (light)         |
| Persistence  | In-memory (MVP) -> Timescale or ClickHouse later |
| Testing      | pytest                      |
| Lint/Format  | ruff + black style          |
| Typing       | mypy                        |
| Frontend     | React + Vite (placeholder)  |
| CI           | GitHub Actions              |

## 5. Ingestion Strategy
1. Bootstrap symbols/universe (Polygon equities, Binance spot pairs)
2. Historical backfill (configurable date ranges)
3. Live polling or websocket subscription (future)
4. Normalize to unified:
   - Bar (symbol, interval, open/high/low/close, volume, start/end timestamp, source)
   - Trade (symbol, price, size, ts)
5. Store in pluggable backend (abstract interface today)

## 6. Normalization
- Symbol canonical format: {EXCHANGE}:{BASE}{QUOTE} or TICKER for equities
- Timezone normalization to UTC
- Numeric precision handling

## 7. Running (Local)
```bash
# Backend (dev)
cd backend
pip install --upgrade pip
pip install -e .[dev]
uvicorn market_intel.api.main:app --reload

# Frontend (placeholder)
cd frontend
npm install
npm run dev
```

## 8. Tests
```bash
pytest -q
```

## 9. CI
- ruff lint
- mypy (strict-ish baseline)
- pytest
- (Later) build & publish Docker images

## 10. Roadmap (Short-Term)
- [ ] Complete basic ingestion (Polygon daily bars)
- [ ] Add Binance kline ingestion
- [ ] Persist normalized bars (memory -> DB abstraction)
- [ ] Expose /health and /bars endpoints
- [ ] Add WebSocket streaming (placeholder event source)
- [ ] Evaluate TimescaleDB vs ClickHouse
- [ ] Backfill orchestration
- [ ] Add strategy/backtesting module skeleton

## 11. Contributing
Branch naming:
- feature/<scope>
- fix/<issue>
- chore/<task>
- docs/<topic>
- refactor/<area>

PR checklist:
- Tests passing
- Lint & type-check clean
- Updated docs if schema/behavior changes

## 12. License
(Choose and update LICENSE file: MIT recommended for simplicity.)

## 13. Disclaimer
Ensure compliance with data provider terms and any regulatory constraints on market data distribution.

---
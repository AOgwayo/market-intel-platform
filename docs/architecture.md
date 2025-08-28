# Architecture Overview

(Expand as system evolves.)

## Layers
- Ingestion Adapters
- Normalization
- Storage Abstraction
- API / Streaming
- Consumers (frontend, notebooks, strategies)

## Scaling Considerations
- Replace in-memory store with TimescaleDB or ClickHouse
- Add message broker (Kafka / Redpanda) for ingestion fanout
- Horizontal scale ingestion workers
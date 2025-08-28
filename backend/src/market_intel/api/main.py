from __future__ import annotations
from fastapi import FastAPI
from market_intel.logging_config import configure_logging

app = FastAPI(title="Market Intel API", version="0.1.0")
configure_logging()

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
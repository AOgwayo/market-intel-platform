-- Migration: Add unique index on bars table for idempotent upserts
-- Date: 2025-09-01
-- Description: Creates a unique index on (symbol, timeframe, ts) columns to enable
--              idempotent bar upserts using ON CONFLICT DO UPDATE patterns.

-- IMPORTANT: Pre-migration duplicate check and cleanup guidance
-- 
-- Before applying this migration, check for and resolve any existing duplicates:
--
-- 1. Check for existing duplicates:
--    SELECT symbol, timeframe, ts, COUNT(*) as duplicate_count
--    FROM bars 
--    GROUP BY symbol, timeframe, ts 
--    HAVING COUNT(*) > 1
--    ORDER BY duplicate_count DESC, symbol, timeframe, ts;
--
-- 2. If duplicates exist, choose resolution strategy:
--    a) Keep latest by id: DELETE FROM bars WHERE id NOT IN (
--         SELECT MAX(id) FROM bars GROUP BY symbol, timeframe, ts
--       );
--    b) Keep latest by updated_at (if column exists): DELETE FROM bars WHERE id NOT IN (
--         SELECT DISTINCT ON (symbol, timeframe, ts) id
--         FROM bars ORDER BY symbol, timeframe, ts, updated_at DESC
--       );
--    c) Manual review for critical duplicates with different OHLCV data
--
-- 3. After cleanup, verify no duplicates remain before applying this migration.

-- Create unique index using CONCURRENTLY to minimize table locking
-- Note: CONCURRENTLY requires the migration to be run outside a transaction
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_bars_symbol_timeframe_ts_unique
ON bars (symbol, timeframe, ts);

-- Alternative: If running within a transaction or CONCURRENTLY is not supported,
-- use the standard approach (uncomment and use instead):
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_bars_symbol_timeframe_ts_unique
-- ON bars (symbol, timeframe, ts);

-- Post-migration notes:
-- 
-- 1. This index enables idempotent upsert patterns such as:
--    INSERT INTO bars (symbol, timeframe, ts, open, high, low, close, volume, created_at, updated_at)
--    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
--    ON CONFLICT (symbol, timeframe, ts)
--    DO UPDATE SET
--      open = EXCLUDED.open,
--      high = EXCLUDED.high,
--      low = EXCLUDED.low,
--      close = EXCLUDED.close,
--      volume = EXCLUDED.volume,
--      updated_at = NOW()
--    WHERE bars.updated_at < EXCLUDED.updated_at; -- Optional: only update if newer
--
-- 2. The index will also improve query performance for:
--    - Point lookups: WHERE symbol = ? AND timeframe = ? AND ts = ?
--    - Range queries: WHERE symbol = ? AND timeframe = ? AND ts BETWEEN ? AND ?
--    - Time series analysis grouped by symbol and timeframe
--
-- 3. Index maintenance considerations:
--    - Monitor index size growth with high-frequency data ingestion
--    - Consider partitioning strategies for very large datasets
--    - Evaluate composite index effectiveness vs separate indexes based on query patterns

-- Rollback instructions (if needed):
-- DROP INDEX IF EXISTS idx_bars_symbol_timeframe_ts_unique;
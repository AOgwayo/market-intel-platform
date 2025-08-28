from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import sys
import os
import asyncio
import logging

# Add backend to path
sys.path.append('/opt/airflow/backend')

from backend.app.core.config import settings
from backend.app.ingestion.polygon_equities import ingest_historical_minute_bars
from backend.app.models.database import SessionLocal
from backend.app.models.market_data import MarketBar

logger = logging.getLogger(__name__)


def check_polygon_api_key():
    """Check if Polygon API key is configured."""
    if not settings.polygon_api_key:
        logger.warning("POLYGON_API_KEY not configured, DAG will be skipped")
        return False
    return True


def get_last_ingested_timestamp(symbol: str) -> datetime:
    """Get the last ingested timestamp for a symbol."""
    session = SessionLocal()
    try:
        last_bar = session.query(MarketBar).filter(
            MarketBar.symbol == symbol,
            MarketBar.source == 'polygon',
            MarketBar.timeframe == '1m'
        ).order_by(MarketBar.timestamp.desc()).first()
        
        if last_bar:
            return last_bar.timestamp + timedelta(minutes=1)
        else:
            # Default to 7 days ago if no data
            return datetime.now() - timedelta(days=7)
    finally:
        session.close()


def ingest_polygon_data(**context):
    """Task function to ingest Polygon minute data."""
    
    # Check API key
    if not check_polygon_api_key():
        logger.info("Skipping ingestion due to missing API key")
        return 0
    
    symbols = settings.equity_symbols_list
    total_ingested = 0
    
    for symbol in symbols:
        try:
            # Get last timestamp for incremental ingestion
            start_time = get_last_ingested_timestamp(symbol)
            end_time = datetime.now()
            
            # Skip if we're already up to date (within last 15 minutes)
            if (end_time - start_time).total_seconds() < 900:
                logger.info(f"Data for {symbol} is up to date")
                continue
            
            logger.info(f"Ingesting {symbol} data from {start_time} to {end_time}")
            
            # Run async ingestion in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                count = loop.run_until_complete(
                    ingest_historical_minute_bars([symbol], start_time, end_time)
                )
                total_ingested += count
                logger.info(f"Ingested {count} bars for {symbol}")
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error ingesting data for {symbol}: {e}")
    
    logger.info(f"Total bars ingested: {total_ingested}")
    return total_ingested


def trigger_strategy_run(**context):
    """Optionally trigger strategy runs after data ingestion."""
    # This is a placeholder for strategy runner integration
    # The actual implementation would depend on the strategy runner design
    
    ingested_count = context['task_instance'].xcom_pull(task_ids='ingest_polygon_minute_data')
    
    if ingested_count and ingested_count > 0:
        logger.info(f"Would trigger strategy run for {ingested_count} new bars")
        # TODO: Implement strategy runner call
        # run_strategies_for_symbols(settings.equity_symbols_list)
    else:
        logger.info("No new data ingested, skipping strategy run")


# DAG configuration
default_args = {
    'owner': 'market-intel',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Create DAG
dag = DAG(
    'polygon_equities_minute_ingest',
    default_args=default_args,
    description='Ingest minute-level equity data from Polygon.io',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    max_active_runs=1,
    tags=['ingestion', 'polygon', 'equities']
)

# Check if API key is configured
check_api_key_task = PythonOperator(
    task_id='check_polygon_api_key',
    python_callable=check_polygon_api_key,
    dag=dag
)

# Main ingestion task
ingest_data_task = PythonOperator(
    task_id='ingest_polygon_minute_data',
    python_callable=ingest_polygon_data,
    dag=dag
)

# Strategy trigger task (optional)
trigger_strategies_task = PythonOperator(
    task_id='trigger_strategy_run',
    python_callable=trigger_strategy_run,
    dag=dag
)

# Skip task for when API key is not configured
skip_task = DummyOperator(
    task_id='skip_ingestion',
    dag=dag
)

# Set up task dependencies with conditional execution
check_api_key_task >> [ingest_data_task, skip_task]
ingest_data_task >> trigger_strategies_task
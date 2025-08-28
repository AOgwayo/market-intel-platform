"""
Intraday data ingestion DAG.

This DAG handles real-time and intraday market data ingestion:
1. Start/monitor WebSocket connections
2. Process streaming data
3. Generate alerts for significant market events
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging

# Default arguments for the DAG
default_args = {
    'owner': 'market-intel-platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

# Create the DAG
dag = DAG(
    'ingest_intraday',
    default_args=default_args,
    description='Intraday market data ingestion and monitoring',
    schedule_interval=timedelta(minutes=15),  # Run every 15 minutes during market hours
    catchup=False,
    tags=['market-data', 'intraday', 'streaming'],
)


def check_market_hours(**context):
    """Check if market is currently open."""
    execution_time = context['execution_date']
    
    # Simple market hours check (9:30 AM - 4:00 PM ET on weekdays)
    # In production, you'd use a proper market calendar library
    weekday = execution_time.weekday()  # 0 = Monday
    hour = execution_time.hour
    
    is_market_day = weekday < 5  # Monday-Friday
    is_market_hours = 9 <= hour < 16  # Simplified hours check
    
    market_open = is_market_day and is_market_hours
    
    logging.info(f"Market open check: {market_open} (weekday: {weekday}, hour: {hour})")
    
    if not market_open:
        logging.info("Market is closed, skipping intraday ingestion")
        return "market_closed"
    
    return "market_open"


def start_websocket_ingestion(**context):
    """Start or check WebSocket data ingestion."""
    
    logging.info("Starting WebSocket ingestion monitoring...")
    
    # In a real implementation, this would:
    # 1. Check if WebSocket connections are active
    # 2. Start new connections if needed
    # 3. Monitor connection health
    # 4. Restart failed connections
    
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']
    
    for symbol in symbols:
        logging.info(f"WebSocket connection active for {symbol}")
    
    return f"Monitored {len(symbols)} WebSocket connections"


def process_streaming_data(**context):
    """Process recent streaming data."""
    
    logging.info("Processing streaming market data...")
    
    # This would typically:
    # 1. Read recent streaming data from buffer/queue
    # 2. Aggregate into minute/5-minute bars
    # 3. Calculate real-time indicators
    # 4. Store processed data
    
    processed_records = 150  # Mock count
    logging.info(f"Processed {processed_records} streaming records")
    
    return f"Processed {processed_records} records"


def check_market_alerts(**context):
    """Check for significant market events and generate alerts."""
    
    logging.info("Checking for market alerts...")
    
    # Mock alert checks
    alert_checks = [
        "Unusual volume spikes",
        "Significant price movements",
        "Technical pattern breakouts",
        "News sentiment changes"
    ]
    
    alerts_triggered = 0
    
    for check in alert_checks:
        # Mock alert logic
        logging.info(f"Checking: {check} - No alerts")
    
    logging.info(f"Market alert check completed. {alerts_triggered} alerts triggered.")
    
    return f"Generated {alerts_triggered} alerts"


def cleanup_old_data(**context):
    """Clean up old intraday data to manage storage."""
    
    logging.info("Cleaning up old intraday data...")
    
    # This would typically:
    # 1. Remove raw streaming data older than X days
    # 2. Archive important data
    # 3. Optimize database performance
    
    cleaned_records = 500  # Mock count
    logging.info(f"Cleaned up {cleaned_records} old records")
    
    return f"Cleaned {cleaned_records} records"


# Define tasks
market_hours_task = PythonOperator(
    task_id='check_market_hours',
    python_callable=check_market_hours,
    dag=dag,
)

websocket_task = PythonOperator(
    task_id='start_websocket_ingestion',
    python_callable=start_websocket_ingestion,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_streaming_data',
    python_callable=process_streaming_data,
    dag=dag,
)

alerts_task = PythonOperator(
    task_id='check_market_alerts',
    python_callable=check_market_alerts,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_data',
    python_callable=cleanup_old_data,
    dag=dag,
)

# Set task dependencies
market_hours_task >> websocket_task >> process_task >> alerts_task >> cleanup_task
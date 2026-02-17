"""
Database connection and schema management.
Uses PostgreSQL with TimescaleDB extension.
"""
import os
from datetime import datetime
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Database connection parameters
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://stockuser:stockpass@localhost:5432/stockdb")

@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database schema."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Enable TimescaleDB extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

            # Create stock_data table (hypertable)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    time TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    open DOUBLE PRECISION NOT NULL,
                    high DOUBLE PRECISION NOT NULL,
                    low DOUBLE PRECISION NOT NULL,
                    close DOUBLE PRECISION NOT NULL,
                    volume BIGINT NOT NULL
                );
            """)

            # Convert to hypertable
            cur.execute("""
                SELECT create_hypertable('stock_data', 'time', 
                    if_not_exists => TRUE, 
                    migrate_data => TRUE);
            """)

            # Create index on symbol
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_data_symbol 
                ON stock_data (symbol, time DESC);
            """)

            # Create indicators table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS indicators (
                    id SERIAL PRIMARY KEY,
                    time TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    indicator_name TEXT NOT NULL,
                    value DOUBLE PRECISION NOT NULL,
                    params JSONB
                );
            """)

            # Create index on indicators
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_indicators_symbol 
                ON indicators (symbol, time DESC);
            """)

            conn.commit()
            print("Database initialized successfully.")

def insert_stock_data(symbol: str, data: List[dict]):
    """Insert stock OHLCV data."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            for bar in data:
                cur.execute("""
                    INSERT INTO stock_data (time, symbol, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (bar['timestamp'], symbol, bar['open'], bar['high'], 
                      bar['low'], bar['close'], bar['volume']))
            conn.commit()

def get_stock_data(symbol: str, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None, 
                   limit: int = 100) -> List[dict]:
    """Retrieve stock data."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM stock_data WHERE symbol = %s"
            params = [symbol]
            
            if start_time:
                query += " AND time >= %s"
                params.append(start_time)
            if end_time:
                query += " AND time <= %s"
                params.append(end_time)
            
            query += " ORDER BY time DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            return cur.fetchall()

if __name__ == "__main__":
    init_db()

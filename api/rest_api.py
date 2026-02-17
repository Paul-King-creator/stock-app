"""
REST API for stock data and indicators.
Uses FastAPI and the indicators module.
"""
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pandas as pd
from mock_provider import get_provider
from models import StockDayData
from indicators.calculator import (
    calculate_sma, calculate_ema, calculate_rsi, 
    calculate_macd, calculate_bollinger_bands, calculate_all_indicators
)

app = FastAPI(title="Stock App API", version="0.2.0")

# Mock Data Provider instance
provider = get_provider()

@app.get("/")
def root():
    return {"message": "Stock App API", "version": "0.2.0"}

@app.get("/stocks/symbols")
def get_symbols():
    """List available stock symbols."""
    return {
        "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META"]
    }

@app.get("/stocks/{symbol}/profile")
def get_stock_profile(symbol: str):
    """Get stock profile/details."""
    profiles = {
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Services"},
        "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
        "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
        "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
        "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
        "META": {"name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Internet Content"}
    }
    return profiles.get(symbol, {"symbol": symbol, "name": f"{symbol} Corp.", "sector": "Unknown"})

@app.get("/stocks/{symbol}/history")
def get_history(
    symbol: str,
    interval: str = Query("1d", regex="^(1m|5m|15m|1h|1d)$"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Fetch historical OHLCV data."""
    days = min(limit, 365)
    data = provider.get_historical_data(symbol, days=days)
    
    return {
        "symbol": symbol,
        "interval": interval,
        "data": [d.to_dict() for d in data]
    }

@app.get("/stocks/{symbol}/indicators")
def get_indicators(
    symbol: str,
    indicators: str = Query("sma", description="Comma-separated: sma,rsi,macd,ema,bb"),
    window: int = Query(20, description="Window size for SMA/EMA/RSI")
):
    """
    Fetch technical indicator data.
    Examples: /stocks/AAPL/indicators?indicators=sma,rsi,macd
    """
    # Get price history as DataFrame
    history = provider.get_historical_data(symbol, days=200)
    df = pd.DataFrame([{
        'date': d.date,
        'open': d.open,
        'high': d.high,
        'low': d.low,
        'close': d.close,
        'volume': d.volume
    } for d in history])
    
    if df.empty:
        return {"error": "No data available"}
    
    result = {"symbol": symbol}
    indicators_list = [i.strip().lower() for i in indicators.split(',')]
    
    close = df['close']
    
    if 'sma' in indicators_list:
        sma = calculate_sma(close, window)
        result['sma'] = [
            {"timestamp": str(df['date'].iloc[i]), "value": round(v, 2)}
            for i, v in enumerate(sma.dropna()) if i >= window-1
        ]
    
    if 'ema' in indicators_list:
        ema = calculate_ema(close, window)
        result['ema'] = [
            {"timestamp": str(df['date'].iloc[i]), "value": round(v, 2)}
            for i, v in enumerate(ema.dropna()) if i >= window-1
        ]
    
    if 'rsi' in indicators_list:
        rsi_window = 14
        rsi = calculate_rsi(close, rsi_window)
        result['rsi'] = [
            {"timestamp": str(df['date'].iloc[i]), "value": round(v, 2)}
            for i, v in enumerate(rsi.dropna()) if i >= rsi_window + window - 2
        ]
    
    if 'macd' in indicators_list:
        macd_line, signal_line, histogram = calculate_macd(close)
        result['macd'] = {
            "line": [
                {"timestamp": str(df['date'].iloc[i]), "value": round(v, 4)}
                for i, v in enumerate(macd_line.dropna()) if i >= 26
            ],
            "signal": [
                {"timestamp": str(df['date'].iloc[i]), "value": round(v, 4)}
                for i, v in enumerate(signal_line.dropna()) if i >= 26
            ],
            "histogram": [
                {"timestamp": str(df['date'].iloc[i]), "value": round(v, 4)}
                for i, v in enumerate(histogram.dropna()) if i >= 26
            ]
        }
    
    if 'bb' in indicators_list:
        sma_bb, upper, lower = calculate_bollinger_bands(close, window)
        result['bollinger_bands'] = {
            "middle": [
                {"timestamp": str(df['date'].iloc[i]), "value": round(v, 2)}
                for i, v in enumerate(sma_bb.dropna()) if i >= window-1
            ],
            "upper": [
                {"timestamp": str(df['date'].iloc[i]), "value": round(v, 2)}
                for i, v in enumerate(upper.dropna()) if i >= window-1
            ],
            "lower": [
                {"timestamp": str(df['date'].iloc[i]), "value": round(v, 2)}
                for i, v in enumerate(lower.dropna()) if i >= window-1
            ]
        }
    
    return result

@app.get("/stocks/{symbol}/signals")
def get_signals(
    symbol: str,
    strategy: str = Query("default", description="Strategy name")
):
    """
    Generate trading signals based on indicators.
    Simple example: SMA crossover, RSI overbought/oversold.
    """
    history = provider.get_historical_data(symbol, days=100)
    df = pd.DataFrame([{
        'date': d.date, 'close': d.close
    } for d in history])
    
    close = df['close']
    
    # Simple signal logic
    sma_fast = calculate_sma(close, 10)
    sma_slow = calculate_sma(close, 50)
    
    # Last values
    fast_last = sma_fast.iloc[-1] if len(sma_fast) > 0 else 0
    slow_last = sma_slow.iloc[-1] if len(sma_slow) > 0 else 0
    
    rsi = calculate_rsi(close, 14)
    rsi_last = rsi.iloc[-1] if len(rsi) > 0 else 50
    
    # Generate signals
    signals = []
    
    # SMA Crossover
    if fast_last > slow_last:
        signals.append({"type": "bullish", "indicator": "sma_crossover", "message": "Golden Cross detected"})
    elif fast_last < slow_last:
        signals.append({"type": "bearish", "indicator": "sma_crossover", "message": "Death Cross detected"})
    
    # RSI
    if rsi_last < 30:
        signals.append({"type": "bullish", "indicator": "rsi", "message": f"RSI oversold ({round(rsi_last, 2)})"})
    elif rsi_last > 70:
        signals.append({"type": "bearish", "indicator": "rsi", "message": f"RSI overbought ({round(rsi_last, 2)})"})
    
    return {
        "symbol": symbol,
        "signals": signals,
        "indicators": {
            "sma_fast": round(fast_last, 2),
            "sma_slow": round(slow_last, 2),
            "rsi": round(rsi_last, 2)
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Technical indicators calculation module.
Implements SMA, EMA, RSI, MACD using Pandas.
"""
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

def calculate_sma(prices: pd.Series, window: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return prices.rolling(window=window).mean()

def calculate_ema(prices: pd.Series, window: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return prices.ewm(span=window, adjust=False).mean()

def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence)."""
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices: pd.Series, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands."""
    sma = calculate_sma(prices, window)
    std = prices.rolling(window=window).std()
    
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    return sma, upper_band, lower_band

def calculate_all_indicators(df: pd.DataFrame, symbol: str) -> Dict:
    """
    Calculate all technical indicators for a given dataframe.
    Expects dataframe with 'close' column.
    """
    if 'close' not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")
    
    close = df['close']
    
    indicators = {
        'symbol': symbol,
        'sma_20': calculate_sma(close, 20).dropna().to_dict(),
        'sma_50': calculate_sma(close, 50).dropna().to_dict(),
        'sma_200': calculate_sma(close, 200).dropna().to_dict(),
        'ema_12': calculate_ema(close, 12).dropna().to_dict(),
        'ema_26': calculate_ema(close, 26).dropna().to_dict(),
        'rsi_14': calculate_rsi(close, 14).dropna().to_dict(),
    }
    
    macd_line, signal_line, histogram = calculate_macd(close)
    indicators['macd'] = {
        'line': macd_line.dropna().to_dict(),
        'signal': signal_line.dropna().to_dict(),
        'histogram': histogram.dropna().to_dict()
    }
    
    sma_bb, upper_bb, lower_bb = calculate_bollinger_bands(close)
    indicators['bollinger_bands'] = {
        'middle': sma_bb.dropna().to_dict(),
        'upper': upper_bb.dropna().to_dict(),
        'lower': lower_bb.dropna().to_dict()
    }
    
    return indicators

if __name__ == "__main__":
    # Test with sample data
    import random
    prices = pd.Series([random.uniform(100, 110) for _ in range(100)])
    
    print("SMA 20:", calculate_sma(prices, 20).iloc[-1])
    print("EMA 12:", calculate_ema(prices, 12).iloc[-1])
    print("RSI 14:", calculate_rsi(prices, 14).iloc[-1])
    
    macd_line, signal_line, histogram = calculate_macd(prices)
    print("MACD:", macd_line.iloc[-1], "Signal:", signal_line.iloc[-1])

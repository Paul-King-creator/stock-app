"""
Models for stock data.
Defines the core data structures for the stock application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StockDayData:
    """Historical daily OHLCV data for a stock."""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "date": self.date.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

@dataclass
class StockRealtimeData:
    """Real-time tick data for a stock."""
    symbol: str
    timestamp: datetime
    price: float
    bid: float
    ask: float
    volume: int

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "bid": self.bid,
            "ask": self.ask,
            "volume": self.volume
        }

@dataclass
class OHLCVBar:
    """OHLCV bar for charting."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

@dataclass
class Indicator:
    """Technical indicator data point."""
    name: str
    symbol: str
    timestamp: datetime
    value: float
    params: Optional[dict] = None

    def to_dict(self):
        return {
            "name": self.name,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "params": self.params or {}
        }

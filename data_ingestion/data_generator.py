"""
Data generator for mock stock data.
Generates realistic-looking random walk data for simulation.
"""
import random
import time
from datetime import datetime, timedelta
from typing import List
from .models import StockDayData, StockRealtimeData, OHLCVBar

class DataGenerator:
    def __init__(self, initial_price: float = 100.0, volatility: float = 0.02):
        self.initial_price = initial_price
        self.volatility = volatility # Daily volatility
        self.current_price = initial_price

    def generate_day_data(self, symbol: str, days: int = 30) -> List[StockDayData]:
        """Generate historical daily data."""
        data = []
        current_price = self.initial_price
        start_date = datetime.now() - timedelta(days=days)

        for i in range(days):
            # Random walk
            change_pct = random.gauss(0, self.volatility)
            open_price = current_price
            close_price = open_price * (1 + change_pct)
            
            # Generate high/low based on open/close
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
            
            volume = int(random.uniform(1000000, 10000000))
            
            date = start_date + timedelta(days=i)
            
            day_data = StockDayData(
                symbol=symbol,
                date=date,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume
            )
            data.append(day_data)
            current_price = close_price
            
        self.current_price = current_price
        return data

    def generate_realtime_tick(self, symbol: str) -> StockRealtimeData:
        """Generate a single real-time tick."""
        # Smaller volatility for intraday
        change_pct = random.gauss(0, 0.0005)
        price = self.current_price * (1 + change_pct)
        
        spread = price * 0.0001 # 0.01% spread
        
        tick = StockRealtimeData(
            symbol=symbol,
            timestamp=datetime.now(),
            price=round(price, 2),
            bid=round(price - spread, 2),
            ask=round(price + spread, 2),
            volume=random.randint(100, 1000)
        )
        self.current_price = price
        return tick

    def generate_ohlcv_bar(self, symbol: str, interval_minutes: int = 1) -> OHLCVBar:
        """Generate an OHLCV bar for the current minute."""
        # Simplified: just using the current tick data to form a bar
        # In a real system, we'd aggregate ticks over the interval
        tick = self.generate_realtime_tick(symbol)
        return OHLCVBar(
            timestamp=tick.timestamp,
            open=tick.price,
            high=tick.price,
            low=tick.price,
            close=tick.price,
            volume=tick.volume
        )

# Example usage
if __name__ == "__main__":
    gen = DataGenerator(initial_price=150.0)
    history = gen.generate_day_data("AAPL", days=10)
    for d in history:
        print(f"{d.date}: O:{d.open} H:{d.high} L:{d.low} C:{d.close} V:{d.volume}")
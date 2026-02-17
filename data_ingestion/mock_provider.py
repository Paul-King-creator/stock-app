"""
Mock data provider.
Simulates connecting to an external market data API.
"""
from datetime import datetime
from typing import List, Dict
from .data_generator import DataGenerator
from models import StockDayData, StockRealtimeData

class MockDataProvider:
    def __init__(self):
        self.generators = {} # symbol -> DataGenerator

    def _get_generator(self, symbol: str) -> DataGenerator:
        if symbol not in self.generators:
            # Assign a random starting price between 50 and 500
            import random
            initial_price = random.uniform(50, 500)
            self.generators[symbol] = DataGenerator(initial_price=initial_price)
        return self.generators[symbol]

    def get_historical_data(self, symbol: str, days: int = 30) -> List[StockDayData]:
        """Fetch historical daily data."""
        gen = self._get_generator(symbol)
        return gen.generate_day_data(symbol, days=days)

    def get_realtime_quote(self, symbol: str) -> StockRealtimeData:
        """Fetch a single real-time quote."""
        gen = self._get_generator(symbol)
        return gen.generate_realtime_tick(symbol)

    def subscribe(self, symbols: List[str], callback):
        """Subscribe to real-time updates for symbols."""
        # In a real implementation, this would connect to a websocket
        # Here we just simulate it
        import time
        while True:
            for symbol in symbols:
                quote = self.get_realtime_quote(symbol)
                callback(quote)
            time.sleep(1) # Update every second

# Global instance
provider = MockDataProvider()

def get_provider() -> MockDataProvider:
    return provider

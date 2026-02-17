# Stock Web App: Architecture & Design Document

## 1. Architecture Overview

Modulare Architektur mit folgenden Komponenten:

```
Data Ingestion (External APIs) -> Data Storage -> Real-time Streaming -> API Layer -> UI
```

## 2. Tech Stack

- Backend: Python + FastAPI
- DB: PostgreSQL + TimescaleDB
- Realtime: WebSockets (FastAPI native)
- Frontend: React + TypeScript
- Charting: TradingView Lightweight Charts / Chart.js

## 3. Datenmodelle

### StockDayData (OHLCV)
```json
{
  "symbol": "AAPL",
  "date": "2026-02-16",
  "open": 170.50,
  "high": 172.00,
  "low": 169.75,
  "close": 171.25,
  "volume": 50000000
}
```

### StockRealtimeData
```json
{
  "symbol": "AAPL",
  "timestamp": "2026-02-16T22:30:00Z",
  "price": 171.30,
  "change": 1.05,
  "change_percent": "0.62%"
}
```

## 4. Module Interfaces

### DataIngestionService
```python
class DataIngestionService:
    def fetch_historical_data(self, symbol: str, start_date: str, end_date: str) -> List[StockDayData]: ...
    def fetch_realtime_quote(self, symbol: str) -> StockRealtimeData: ...
    def get_supported_symbols(self) -> List[str]: ...
```

### DataStorageService
```python
class DataStorageService:
    def save_daily_data(self, data: List[StockDayData]) -> None: ...
    def save_realtime_snapshot(self, data: StockRealtimeData) -> None: ...
    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> List[StockDayData]: ...
    def get_latest_realtime_data(self, symbol: str) -> Optional[StockRealtimeData]: ...
```

### RealtimeStreamingService
```python
class RealtimeStreamingService:
    async def subscribe(self, client_id: str, symbol: str) -> None: ...
    async def unsubscribe(self, client_id: str, symbol: str) -> None: ...
    async def broadcast_update(self, data: StockRealtimeData) -> None: ...
```

### API Endpoints (FastAPI)
```python
@app.get("/api/stocks/{symbol}")           # Latest quote
@app.get("/api/stocks/{symbol}/history")   # Historical OHLCV
@app.get("/api/symbols")                   # All tracked symbols
@app.websocket("/ws")                      # Realtime stream
```

## 5. UI Skeleton

- Dashboard: Watchlist, Marktueberblick, Portfolio-Summary
- Chart View: Interaktiver OHLCV-Chart mit Indikatoren
- Trading Panel: Paper Trading Order Entry
- Signal Feed: Erkannte Patterns + Trade Signals

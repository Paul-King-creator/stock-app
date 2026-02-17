import uvicorn # Using FastAPI for API
from fastapi import FastAPI, HTTPException, Request
from portfolio import PortfolioManager
from execution import ExecutionEngine
from pnl import PnLCalculator
from orders import OrderType, OrderSide
from typing import Dict, Any

# This API is a minimal example and would typically be part of a larger application
# or integrated with a signal generation service.

# Assume these are initialized globally or passed in a real application context
# For this skeleton, we'll create them here.
# In a real app, these would be managed and passed appropriately.
# Example:
# portfolio_manager = PortfolioManager(initial_cash=100000.0)
# execution_engine = ExecutionEngine(portfolio_manager)
# pnl_calculator = PnLCalculator(portfolio_manager)

# For demonstration purposes, we'll define placeholder objects
# In a real scenario, the FastAPI app would likely be initialized elsewhere
# and these services would be dependency-injected or globally accessible.

app = FastAPI()

# Placeholder for services - this would be a real instance in a running app
class MockServices:
    def __init__(self):
        self.portfolio_manager = PortfolioManager(initial_cash=100000.0)
        self.execution_engine = ExecutionEngine(self.portfolio_manager)
        self.pnl_calculator = PnLCalculator(self.portfolio_manager)

# Global or managed instance of services
# In a real application, use dependency injection.
# This is a simplified approach for a skeleton.
services = MockServices()

@app.get("/")
def read_root():
    return {"message": "Paper Trading Engine API"}

@app.get("/portfolio")
def get_portfolio_details():
    """Returns current cash and positions."""
    return {
        "cash": services.portfolio_manager.cash,
        "positions": services.portfolio_manager.get_positions_df().to_dict(orient='records')
    }

@app.get("/portfolio/value")
def get_portfolio_value(current_prices_json: str = '{}'):
    """Returns the total portfolio value, optionally using provided current prices."""
    try:
        current_prices = eval(current_prices_json) # Simple eval for demo; use json.loads in production
        if not isinstance(current_prices, dict):
            raise ValueError("Invalid JSON format for current_prices")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid current_prices parameter: {e}")
        
    value = services.portfolio_manager.get_portfolio_value(current_prices)
    return {"portfolio_value": value}

@app.get("/orders/open")
def get_open_orders():
    """Returns all currently open orders."""
    return services.execution_engine.get_open_orders_df().to_dict(orient='records')

@app.post("/orders")
def place_order(order_data: Dict[str, Any]):
    """
    Places a new order.
    Expected JSON format:
    {
        "symbol": "AAPL",
        "order_type": "MARKET" or "LIMIT" or "STOP_LOSS",
        "side": "BUY" or "SELL",
        "quantity": 10.5,
        "price": 150.0,       // Required for LIMIT order
        "stop_price": 145.0,  // Required for STOP_LOSS order
        "timestamp": "2023-10-27T10:00:00Z" // ISO format timestamp
    }
    """
    try:
        symbol = order_data['symbol']
        order_type_str = order_data['order_type'].upper()
        side_str = order_data['side'].upper()
        quantity = float(order_data['quantity'])
        price = float(order_data.get('price', 0)) if order_data.get('price') is not None else None
        stop_price = float(order_data.get('stop_price', 0)) if order_data.get('stop_price') is not None else None
        timestamp = order_data.get('timestamp') # For simulation, actual timestamp might be system time

        order_type = OrderType[order_type_str]
        side = OrderSide[side_str]

        if (order_type == OrderType.LIMIT or order_type == OrderType.STOP_LOSS) and price is None:
            raise ValueError(f"{order_type.value} order requires a 'price' parameter.")
        if order_type == OrderType.STOP_LOSS and stop_price is None:
            raise ValueError(f"{order_type.value} order requires a 'stop_price' parameter.")
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        # In a real system, you'd use the `timestamp` from the input for simulation.
        # For this example, we will use a placeholder or the current time if not provided.
        # If timestamp is crucial for execution logic, it MUST be provided.

        order_id = services.execution_engine.place_order(
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            timestamp=timestamp # Pass the timestamp from request
        )
        return {"message": "Order placed successfully", "order_id": order_id}

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid order parameter: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@app.delete("/orders/{order_id}")
def cancel_order(order_id: str):
    """Cancels an existing open order."""
    success = services.execution_engine.cancel_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found or could not be cancelled.")
    return {"message": f"Order {order_id} cancelled successfully."}

@app.post("/market_data")
def receive_market_data(data: Dict[str, Any]):
    """Endpoint to receive market data ticks and trigger order processing."""
    # Expects data like:
    # {
    #   "timestamp": "2023-10-27T10:01:00Z",
    #   "symbol": "AAPL",
    #   "current_price": 155.50,
    #   "bid_price": 155.48,
    #   "ask_price": 155.52
    # }
    try:
        timestamp = data['timestamp']
        symbol = data['symbol']
        current_price = float(data['current_price'])
        bid_price = float(data.get('bid_price', current_price)) # Default to current_price if not provided
        ask_price = float(data.get('ask_price', current_price)) # Default to current_price if not provided

        filled_orders = services.execution_engine.process_market_data(
            timestamp=timestamp,
            symbol=symbol,
            current_price=current_price,
            bid_price=bid_price,
            ask_price=ask_price
        )
        
        # You can add logic here to update portfolio value history
        # based on the final portfolio value after processing this tick.

        return {"message": f"Market data processed for {symbol}. {len(filled_orders)} orders filled/rejected."}

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required market data field: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid market data value: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

# To run this API:
# 1. Save this code as api.py
# 2. Install FastAPI and Uvicorn: pip install fastapi uvicorn
# 3. Run from terminal: uvicorn api:app --reload
# Note: The --reload flag is for development. Remove for production.

# To connect a signal generator:
# A signal generator would call POST /orders to place trades based on its signals.
# It would also need to know the current market prices to make informed decisions,
# which could be obtained via another API call or by subscribing to a market data feed.
# The signal generator needs to POST market data to /market_data endpoint to trigger order fills.

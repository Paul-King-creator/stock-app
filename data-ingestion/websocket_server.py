"""
WebSocket server for real-time stock data streaming.
Uses asyncio and websockets library.
"""
import asyncio
import json
import websockets
from datetime import datetime
from typing import Set
from mock_provider import get_provider

# Connected clients
connected_clients: Set = set()

async def handle_client(websocket, path):
    """Handle incoming WebSocket client connections."""
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Parse message
            data = json.loads(message)
            action = data.get("action")
            
            if action == "subscribe":
                symbol = data.get("symbol")
                if symbol:
                    await websocket.send(json.dumps({
                        "status": "subscribed",
                        "symbol": symbol
                    }))
                    # Start streaming for this symbol (simplified)
                    asyncio.create_task(stream_symbol(websocket, symbol))
                    
            elif action == "unsubscribe":
                # Logic to stop streaming would go here
                await websocket.send(json.dumps({"status": "unsubscribed"}))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def stream_symbol(websocket, symbol: str):
    """Stream real-time data for a symbol to a specific client."""
    provider = get_provider()
    try:
        while True:
            quote = provider.get_realtime_quote(symbol)
            await websocket.send(json.dumps(quote.to_dict()))
            await asyncio.sleep(1) # 1 second interval
    except websockets.exceptions.ConnectionClosed:
        pass

async def broadcast_to_all(data: dict):
    """Broadcast data to all connected clients."""
    if connected_clients:
        message = json.dumps(data)
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )

async def start_server(host: str = "localhost", port: int = 8765):
    """Start the WebSocket server."""
    async with websockets.serve(handle_client, host, port):
        print(f"WebSocket server started on ws://{host}:{port}")
        await asyncio.Future() # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Server stopped.")

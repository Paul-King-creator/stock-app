# Paper Trading Engine

This project provides a skeleton for a virtual paper trading engine. It includes components for portfolio management, order execution, P&L calculation, trade history logging, and performance metrics.

## Features

- **Virtual Portfolio Management:** Track cash and asset holdings.
- **Order Types:** Market, Limit, and Stop-Loss orders.
- **Execution Logic:** Simulate trade execution based on market data.
- **P&L Calculation:** Real-time and historical profit/loss tracking.
- **Trade History:** Comprehensive logging of all trades.
- **Performance Metrics:** Sharpe Ratio, Win Rate, Drawdown, etc.
- **API Endpoints:** Interface for connecting signal generation systems.

## Setup

To set up and run the engine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd stock-app/paper-trading
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` will be created as part of the project setup.)*
3.  **Run the engine:**
    ```bash
    python main.py
    ```

## Code Structure

-   `portfolio.py`: Manages virtual portfolio state.
-   `orders.py`: Defines order types and logic.
-   `execution.py`: Handles order execution simulation.
-   `pnl.py`: Calculates profit and loss.
-   `trade_history.py`: Logs trade details.
-   `performance_metrics.py`: Computes performance statistics.
-   `api.py`: Provides API endpoints for signal integration.
-   `main.py`: Main application entry point.
-   `requirements.txt`: Project dependencies.

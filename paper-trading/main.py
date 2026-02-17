import datetime
import pandas as pd
import time

from portfolio import PortfolioManager
from execution import ExecutionEngine
from pnl import PnLCalculator
from trade_history import TradeHistoryLogger
from performance_metrics import PerformanceMetrics, calculate_sharpe_ratio, calculate_max_drawdown # Import helper functions if needed directly

# Sample Market Data - In a real system, this would come from a live feed or API
# This simulates a sequence of price changes for demonstration.
sample_market_data = [
    {'timestamp': '2026-02-16 09:30:00', 'symbol': 'AAPL', 'current_price': 150.00, 'bid_price': 149.99, 'ask_price': 150.01},
    {'timestamp': '2026-02-16 09:30:15', 'symbol': 'AAPL', 'current_price': 150.10, 'bid_price': 150.09, 'ask_price': 150.11},
    {'timestamp': '2026-02-16 09:31:00', 'symbol': 'AAPL', 'current_price': 150.50, 'bid_price': 150.49, 'ask_price': 150.51},
    {'timestamp': '2026-02-16 09:32:00', 'symbol': 'AAPL', 'current_price': 149.80, 'bid_price': 149.79, 'ask_price': 149.81},
    {'timestamp': '2026-02-16 09:33:00', 'symbol': 'AAPL', 'current_price': 149.50, 'bid_price': 149.49, 'ask_price': 149.51},
    {'timestamp': '2026-02-16 09:34:00', 'symbol': 'AAPL', 'current_price': 151.00, 'bid_price': 150.99, 'ask_price': 151.01},
    {'timestamp': '2026-02-16 09:35:00', 'symbol': 'AAPL', 'current_price': 151.20, 'bid_price': 151.19, 'ask_price': 151.21},
    {'timestamp': '2026-02-16 09:36:00', 'symbol': 'AAPL', 'current_price': 150.80, 'bid_price': 150.79, 'ask_price': 150.81},
    {'timestamp': '2026-02-16 09:37:00', 'symbol': 'GOOG', 'current_price': 2700.00, 'bid_price': 2699.90, 'ask_price': 2700.10},
    {'timestamp': '2026-02-16 09:38:00', 'symbol': 'GOOG', 'current_price': 2705.00, 'bid_price': 2704.90, 'ask_price': 2705.10},
    {'timestamp': '2026-02-16 09:39:00', 'symbol': 'AAPL', 'current_price': 150.90, 'bid_price': 150.89, 'ask_price': 150.91},
    {'timestamp': '2026-02-16 09:40:00', 'symbol': 'GOOG', 'current_price': 2698.00, 'bid_price': 2697.90, 'ask_price': 2698.10},
]

def run_simulation(market_data, initial_cash=100000.0):
    print("Starting paper trading simulation...")

    # Initialize components
    portfolio_manager = PortfolioManager(initial_cash=initial_cash)
    execution_engine = ExecutionEngine(portfolio_manager)
    pnl_calculator = PnLCalculator(portfolio_manager)
    trade_history_logger = TradeHistoryLogger(portfolio_manager)
    performance_metrics = PerformanceMetrics(portfolio_manager, trade_history_logger)
    
    # To track portfolio value over time for performance metrics
    portfolio_value_history = []

    # --- Strategy / Order Placement ---
    # This section simulates a trading strategy placing orders.
    # In a real system, this would be driven by signal generation (e.g., from an API).
    
    order_id_buy_limit = None
    order_id_sell_stop_loss = None
    order_id_buy_market = None

    initial_portfolio_value = initial_cash
    current_timestamp_dt = None

    for tick in market_data:
        timestamp_str = tick['timestamp']
        symbol = tick['symbol']
        current_price = tick['current_price']
        bid_price = tick.get('bid_price', current_price)
        ask_price = tick.get('ask_price', current_price)
        
        # Convert timestamp string to datetime object for consistent handling
        current_timestamp_dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        # --- Order Placement Logic (Example Strategy) ---
        if symbol == 'AAPL':
            # Example: Place a limit buy order if AAPL is at 150, and we don't have an open buy yet
            if current_price == 150.00 and order_id_buy_limit is None and not execution_engine.open_orders:
                order_id_buy_limit = execution_engine.place_order(
                    symbol='AAPL', order_type=OrderType.LIMIT, side=OrderSide.BUY,
                    quantity=10, price=149.90, timestamp=timestamp_str 
                ) # Aim to buy slightly lower than current
            
            # Example: Place a stop-loss sell order if price drops below 149.50
            if current_price < 149.50 and order_id_sell_stop_loss is None and order_id_buy_limit and execution_engine.open_orders.get(order_id_buy_limit) and execution_engine.open_orders[order_id_buy_limit].status == OrderStatus.FILLED:
                # Only place stop-loss if we actually boughtAAPL
                order_id_sell_stop_loss = execution_engine.place_order(
                    symbol='AAPL', order_type=OrderType.STOP_LOSS, side=OrderSide.SELL,
                    quantity=10, stop_price=149.50, timestamp=timestamp_str
                )

            # Example: Market buy if price suddenly jumps up (e.g., for a breakout)
            if current_price > 151.00 and order_id_buy_market is None and not execution_engine.open_orders:
                 order_id_buy_market = execution_engine.place_order(
                    symbol='AAPL', order_type=OrderType.MARKET, side=OrderSide.BUY,
                    quantity=5, timestamp=timestamp_str # Market order, price is not needed
                )

        elif symbol == 'GOOG':
            # Example: Simple market buy for GOOG if price is around 2700
            if symbol == 'GOOG' and current_price > 2699.00 and not execution_engine.open_orders:
                 execution_engine.place_order(
                    symbol='GOOG', order_type=OrderType.MARKET, side=OrderSide.BUY,
                    quantity=2, timestamp=timestamp_str
                )

        # --- Process Market Data Tick ---
        # The execution engine processes any pending orders based on this tick's data
        filled_orders_this_tick = execution_engine.process_market_data(
            timestamp=timestamp_str,
            symbol=symbol,
            current_price=current_price,
            bid_price=bid_price,
            ask_price=ask_price
        )
        
        # --- Record Portfolio Value for Metrics ---
        # Get current prices for all held assets to calculate portfolio value
        current_holdings_prices = {}
        for pos_symbol, pos_data in portfolio_manager.positions.items():
            # Try to get the price from the current tick if it matches
            # If not, use the last known price for that symbol
            # A more Robust approach: maintain a dict of last known prices for all symbols
            if pos_symbol == symbol: # If current tick is for an asset we hold
                 current_holdings_prices[pos_symbol] = current_price
            else:
                 # Fallback: look for last price in sample_market_data for this symbol
                 last_price_for_symbol = next((item['current_price'] for item in reversed(market_data[:market_data.index(tick)]) if item['symbol'] == pos_symbol), None)
                 if last_price_for_symbol:
                     current_holdings_prices[pos_symbol] = last_price_for_symbol
        
        # If we don't have prices for all assets, the portfolio value calculation might be less accurate.
        portfolio_value = portfolio_manager.get_portfolio_value(current_holdings_prices)
        
        # Store timestamp (as datetime object for sorting/calculations) and value
        portfolio_value_history.append({'timestamp': current_timestamp_dt, 'portfolio_value': portfolio_value})
        
        # Small delay to simulate time passing between ticks if needed for visibility
        # time.sleep(0.01) # Uncomment for slow-mo visualization

    # --- Simulation End ---
    print("\n--- Simulation Finished ---")

    # Convert history to DataFrame for easier analysis
    portfolio_value_history_df = pd.DataFrame(portfolio_value_history)
    if not portfolio_value_history_df.empty:
        portfolio_value_history_df['timestamp'] = pd.to_datetime(portfolio_value_history_df['timestamp'])

    # --- Display Results ---
    print("\n--- Portfolio Summary ---")
    print(f"Initial Cash: ${initial_portfolio_value:.2f}")
    final_portfolio_value = portfolio_manager.get_portfolio_value(current_holdings_prices if current_timestamp_dt else None) # Use last known prices
    print(f"Final Portfolio Value: ${final_portfolio_value:.2f}")
    print(f"Net Profit/Loss: ${final_portfolio_value - initial_portfolio_value:.2f}\n")

    print("--- Current Positions ---")
    print(portfolio_manager.get_positions_df())
    print("\n")

    print("--- Open Orders ---")
    print(execution_engine.get_open_orders_df())
    print("\n")

    print("--- Trade History (Transactions) ---")
    transaction_history = trade_history_logger.get_trades_df()
    print(transaction_history)
    print("\n")
    
    # --- Performance Metrics Calculation ---
    print("--- Performance Metrics ---")
    
    # Realized PnL
    realized_pnl = pnl_calculator.calculate_realized_pnl()
    print(f"Realized PnL: ${realized_pnl:.2f}")

    # Unrealized PnL (needs current prices, use last known if simulation ended)
    unrealized_pnl = pnl_calculator.calculate_unrealized_pnl(current_prices=current_holdings_prices if current_timestamp_dt else None)
    print(f"Unrealized PnL: ${unrealized_pnl:.2f}")

    # Total PnL = Realized + Unrealized
    total_pnl = realized_pnl + unrealized_pnl
    print(f"Total PnL: ${total_pnl:.2f}\n")

    # Detailed Metrics
    metrics = performance_metrics.calculate_metrics(
        current_prices=current_holdings_prices if current_timestamp_dt else None,
        portfolio_value_history=portfolio_value_history_df
    )
    
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}" if not pd.isna(metrics['sharpe_ratio']) else "Sharpe Ratio: N/A")
    print(f"Win Rate: {metrics['win_rate']:.2f}%" if not pd.isna(metrics['win_rate']) else "Win Rate: N/A")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%" if not pd.isna(metrics['max_drawdown']) else "Max Drawdown: N/A")
    if metrics['max_drawdown_start_date'] and metrics['max_drawdown_end_date']:
        print(f"  (Period: {metrics['max_drawdown_start_date']} to {metrics['max_drawdown_end_date']})")
    print(f"Total Return: {metrics['total_return']:.2f}%" if not pd.isna(metrics['total_return']) else "Total Return: N/A")
    print(f"Annualized Return: {metrics['annualized_return']:.2f}%" if not pd.isna(metrics['annualized_return']) else "Annualized Return: N/A")

if __name__ == "__main__":
    # You can customize initial_cash here
    run_simulation(sample_market_data, initial_cash=100000.0)

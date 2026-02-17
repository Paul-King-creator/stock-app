import pandas as pd
import numpy as np

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    # Assumes 'returns' is a Series of periodic returns (e.g., daily)
    if returns.empty or len(returns) < 2:
        return np.nan
    
    # Annualize (assuming daily returns, multiply by sqrt(252))
    # This makes assumptions about the frequency of 'returns' - adjust if needed.
    avg_return = returns.mean()
    std_dev = returns.std()
    
    if std_dev == 0:
        return np.nan

    # Annualized Sharpe Ratio
    # Typically, Sharpe Ratio needs to be calculated from cumulative portfolio value over time,
    # not just a list of returns, to properly account for compounding and volatility.
    # This is a simplified version.
    return (avg_return * 252 - risk_free_rate) / (std_dev * np.sqrt(252))

def calculate_win_rate(trades_df):
    if trades_df.empty:
        return np.nan
    
    # Need to define what constitutes a "win" and "loss"
    # For simplicity, let's assume 'sell' transactions with a positive PnL relative to 'buy'
    # or simply total revenue from sells > total cost of corresponding buys.
    # This requires careful pairing of trades.
    
    # A more practical approach: If we have a way to calculate PnL per closed trade.
    # Let's assume we can infer PnL for each trade from history.
    # For now, we'll use a placeholder based on types of transactions.
    
    wins = 0
    losses = 0
    
    # This is a simplistic view. A proper calculation requires matching buy/sell pairs.
    # For a trade history that logs completed positions, we could do:
    # trades_df['pnl'] = trades_df['sell_price'] - trades_df['buy_price'] # simplified
    # wins = (trades_df['pnl'] > 0).sum()
    # losses = (trades_df['pnl'] < 0).sum()
    
    # Placeholder: If we can determine net profit for each "completed trade event"
    # For now, it's hard to determine win/loss from individual transactions without pairing.
    # Assuming we can calculate PnL for each *closed trade*
    
    # If we had a df like: TradeID, EntryPrice, ExitPrice, Quantity, PnL
    # wins = (df['PnL'] > 0).sum()
    # losses = (df['PnL'] < 0).sum()
    
    # For now, returning NaN as a direct win rate from history is complex.
    return np.nan 

def calculate_max_drawdown(portfolio_history_df):
    # portfolio_history_df should have 'timestamp' and 'portfolio_value' columns
    if portfolio_history_df.empty or len(portfolio_history_df) < 2:
        return np.nan, None, None

    portfolio_history_df = portfolio_history_df.sort_values('timestamp')
    portfolio_history_df['peak'] = portfolio_history_df['portfolio_value'].cummax()
    portfolio_history_df['drawdown'] = ((portfolio_history_df['portfolio_value'] - portfolio_history_df['peak']) / portfolio_history_df['peak']) * 100

    max_drawdown = portfolio_history_df['drawdown'].min()
    
    if pd.isna(max_drawdown):
        return np.nan, None, None

    # Find the period of max drawdown
    drawdown_periods = portfolio_history_df[portfolio_history_df['drawdown'] == max_drawdown]
    if not drawdown_periods.empty:
        start_date = portfolio_history_df.loc[portfolio_history_df['peak'].idxmax(), 'timestamp']
        end_date = drawdown_periods.iloc[0]['timestamp'] # First occurrence of max drawdown
        return max_drawdown, start_date, end_date
    else:
        return max_drawdown, None, None # Should not happen if max_drawdown is not NaN

class PerformanceMetrics:
    def __init__(self, portfolio_manager, trade_history_logger):
        self.portfolio_manager = portfolio_manager
        self.trade_history_logger = trade_history_logger

    def calculate_metrics(self, current_prices=None, portfolio_value_history=None):
        trades_df = self.trade_history_logger.get_trades_df()
        
        results = {
            "sharpe_ratio": np.nan,
            "win_rate": np.nan,
            "max_drawdown": np.nan,
            "max_drawdown_start_date": None,
            "max_drawdown_end_date": None,
            "total_return": np.nan,
            "annualized_return": np.nan
        }

        # Calculate Total Return
        initial_portfolio_value = self.portfolio_manager.cash # Assuming initial cash is the starting point if no history
        # A better approach: store initial value when engine starts
        # For now, let's assume initial_cash from PortfolioManager is the start
        
        # If portfolio_value_history is provided and has multiple entries, we can calculate returns
        if portfolio_value_history is not None and not portfolio_value_history.empty:
             # Assuming portfolio_value_history is a DataFrame with columns like 'timestamp', 'portfolio_value'
            if 'portfolio_value' in portfolio_value_history.columns and not portfolio_value_history.empty:
                portfolio_value_history = portfolio_value_history.sort_values('timestamp')
                initial_value = portfolio_value_history.iloc[0]['portfolio_value']
                final_value = portfolio_value_history.iloc[-1]['portfolio_value']
                
                if initial_value != 0:
                    total_return = ((final_value - initial_value) / initial_value) * 100
                    results["total_return"] = total_return

                    # Annualized Return (this requires knowing the time duration)
                    # Duration in days
                    time_span_days = (portfolio_value_history.iloc[-1]['timestamp'] - portfolio_value_history.iloc[0]['timestamp']).days
                    if time_span_days > 0:
                        # Formula: ( (1 + Total Return/100) ^ (1 / (time_span_days / 365)) - 1 ) * 100
                        annualized_return = ( (1 + total_return/100)**(365/time_span_days) - 1 ) * 100
                        results["annualized_return"] = annualized_return

                # Calculate Sharpe Ratio from portfolio value history
                # convert portfolio value history to returns
                portfolio_value_history['pct_change'] = portfolio_value_history['portfolio_value'].pct_change()
                results["sharpe_ratio"] = calculate_sharpe_ratio(portfolio_value_history['pct_change'])

                # Calculate Max Drawdown
                max_dd, dd_start, dd_end = calculate_max_drawdown(portfolio_value_history[['timestamp', 'portfolio_value']])
                results["max_drawdown"] = max_dd
                results["max_drawdown_start_date"] = dd_start
                results["max_drawdown_end_date"] = dd_end
        
        # Win Rate requires detailed trade PnL per trade, which is complex to derive directly
        # from current transaction logs without pairing buys/sells for each stock.
        # If TradeHistoryLogger provided a "closed_trades" df with PnL per trade, this would be easier.
        # For now, WIN RATE is left as NaN.
        # results["win_rate"] = calculate_win_rate(trades_df) 

        return results


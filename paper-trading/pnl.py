import pandas as pd

class PnLCalculator:
    def __init__(self, portfolio_manager):
        self.portfolio_manager = portfolio_manager

    def calculate_realized_pnl(self):
        # Realized PnL is calculated from completed buy/sell transactions
        # Sum of (sell_price * quantity - buy_price * quantity) for each completed trade
        realized_pnl = 0.0
        transactions = self.portfolio_manager.get_history_df()
        
        if transactions.empty:
            return 0.0

        # Group by symbol and timestamp to consolidate trades if needed, though history logs individual transactions
        # For simplicity, we'll sum up based on individual transactions log for now
        # PnL for a symbol = (Total Sell Revenue) - (Total Buy Cost)
        
        sells = transactions[transactions['type'] == 'sell']
        buys = transactions[transactions['type'] == 'buy']

        sell_revenue = (sells['quantity'] * sells['price']).sum() - sells['commission'].sum()
        buy_cost = (buys['quantity'] * buys['price']).sum() + buys['commission'].sum()

        realized_pnl = sell_revenue - buy_cost
        return realized_pnl

    def calculate_unrealized_pnl(self, current_prices=None):
        if current_prices is None:
            current_prices = {}
            
        unrealized_pnl = 0.0
        positions_df = self.portfolio_manager.get_positions_df()

        if positions_df.empty:
            return 0.0

        for index, row in positions_df.iterrows():
            symbol = row['Symbol']
            quantity = row['Quantity']
            avg_price = row['Avg Price']
            
            if symbol in current_prices:
                current_price = current_prices[symbol]
                # PnL for a position = (current_price - avg_entry_price) * quantity
                unrealized_pnl += (current_price - avg_price) * quantity
            else:
                # If current price is not available, unrealized PnL for this position is 0
                pass
        
        return unrealized_pnl

    def calculate_total_pnl(self, current_prices=None):
        return self.calculate_realized_pnl() + self.calculate_unrealized_pnl(current_prices)


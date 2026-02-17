import pandas as pd
from collections import defaultdict

class PortfolioManager:
    def __init__(self, initial_cash=100000.0):
        self.cash = initial_cash
        self.positions = defaultdict(lambda: {'quantity': 0.0, 'avg_price': 0.0})
        self.history = [] # To log cash and position changes

    def add_transaction(self, timestamp, type, symbol, quantity, price, commission=0.0):
        transaction = {
            'timestamp': timestamp,
            'type': type, # 'buy' or 'sell'
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'total_cost': quantity * price + commission if type == 'buy' else quantity * price - commission
        }
        self.history.append(transaction)

    def buy(self, timestamp, symbol, quantity, price, commission=0.0):
        cost = quantity * price + commission
        if self.cash >= cost:
            self.cash -= cost
            current_quantity = self.positions[symbol]['quantity']
            current_avg_price = self.positions[symbol]['avg_price']

            new_avg_price = ((current_quantity * current_avg_price) + cost) / (current_quantity + quantity)
            self.positions[symbol]['quantity'] += quantity
            self.positions[symbol]['avg_price'] = new_avg_price
            self.add_transaction(timestamp, 'buy', symbol, quantity, price, commission)
            print(f"Bought {quantity} of {symbol} at {price}. Remaining cash: {self.cash:.2f}")
            return True
        else:
            print(f"Insufficient cash to buy {quantity} of {symbol} at {price}.")
            return False

    def sell(self, timestamp, symbol, quantity, price, commission=0.0):
        if symbol in self.positions and self.positions[symbol]['quantity'] >= quantity:
            revenue = quantity * price - commission
            self.cash += revenue
            self.positions[symbol]['quantity'] -= quantity
            if self.positions[symbol]['quantity'] == 0:
                del self.positions[symbol]
            self.add_transaction(timestamp, 'sell', symbol, quantity, price, commission)
            print(f"Sold {quantity} of {symbol} at {price}. Current cash: {self.cash:.2f}")
            return True
        else:
            print(f"Insufficient quantity of {symbol} to sell {quantity}.")
            return False

    def get_portfolio_value(self, current_prices=None):
        if current_prices is None:
            current_prices = {}
        
        total_value = self.cash
        for symbol, data in self.positions.items():
            if symbol in current_prices:
                total_value += data['quantity'] * current_prices[symbol]
            else:
                # If current price is not available, value it at average entry price
                total_value += data['quantity'] * data['avg_price']
        return total_value

    def get_positions_df(self):
        data = []
        for symbol, pos in self.positions.items():
            data.append({
                'Symbol': symbol,
                'Quantity': pos['quantity'],
                'Avg Price': pos['avg_price']
            })
        return pd.DataFrame(data)

    def get_history_df(self):
        return pd.DataFrame(self.history)


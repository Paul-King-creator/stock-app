from portfolio import PortfolioManager
from orders import Order, OrderType, OrderSide, OrderStatus
import pandas as pd
import uuid

class ExecutionEngine:
    def __init__(self, portfolio_manager: PortfolioManager):
        self.portfolio_manager = portfolio_manager
        self.open_orders = {} # {order_id: Order object}
        self.order_counter = 0

    def _generate_order_id(self):
        self.order_counter += 1
        return f"ORD-{self.order_counter}-{uuid.uuid4().hex[:6]}"

    def place_order(self, symbol, order_type, side, quantity, price=None, stop_price=None, timestamp=None):
        order_id = self._generate_order_id()
        order = Order(order_id, symbol, order_type, side, quantity, price, stop_price, timestamp)
        self.open_orders[order_id] = order
        print(f"Order placed: {order}")
        return order_id

    def process_market_data(self, timestamp, symbol, current_price, bid_price=None, ask_price=None):
        # Process open orders against new market data
        # bid_price is the highest price a buyer is willing to pay
        # ask_price is the lowest price a seller is willing to accept
        
        filled_orders_in_tick = []

        for order_id, order in list(self.open_orders.items()): # Iterate over a copy
            if order.symbol != symbol:
                continue

            filled_now = False

            # Market Order Logic
            if order.order_type == OrderType.MARKET and order.status == OrderStatus.PENDING:
                if order.side == OrderSide.BUY:
                    # Market buy order executes at the ask price
                    execution_price = ask_price if ask_price is not None else current_price
                    if self.portfolio_manager.buy(timestamp, order.symbol, order.quantity, execution_price):
                        order.filled_quantity = order.quantity
                        order.filled_price = execution_price
                        order.status = OrderStatus.FILLED
                        filled_orders_in_tick.append(order)
                        filled_now = True
                        print(f"Market Buy Order Filled: {order_id} at {execution_price}")
                    else:
                        order.status = OrderStatus.REJECTED # Insufficient funds
                        filled_orders_in_tick.append(order)
                        filled_now = True # Rejected is also a terminal state for this tick

                elif order.side == OrderSide.SELL:
                    # Market sell order executes at the bid price
                    execution_price = bid_price if bid_price is not None else current_price
                    if self.portfolio_manager.sell(timestamp, order.symbol, order.quantity, execution_price):
                        order.filled_quantity = order.quantity
                        order.filled_price = execution_price
                        order.status = OrderStatus.FILLED
                        filled_orders_in_tick.append(order)
                        filled_now = True
                        print(f"Market Sell Order Filled: {order_id} at {execution_price}")
                    else:
                        order.status = OrderStatus.REJECTED # Insufficient shares
                        filled_orders_in_tick.append(order)
                        filled_now = True

            # Limit Order Logic
            elif order.order_type == OrderType.LIMIT and order.status == OrderStatus.PENDING:
                if order.side == OrderSide.BUY and order.price >= bid_price: # If limit price is met or better (lower)
                    execution_price = min(order.price, ask_price if ask_price is not None else current_price) # Execute at limit or better
                    if self.portfolio_manager.buy(timestamp, order.symbol, order.quantity, execution_price):
                        order.filled_quantity = order.quantity
                        order.filled_price = execution_price
                        order.status = OrderStatus.FILLED
                        filled_orders_in_tick.append(order)
                        filled_now = True
                        print(f"Limit Buy Order Filled: {order_id} at {execution_price}")
                    else:
                        # This case should ideally not happen if portfolio check is done before
                        order.status = OrderStatus.REJECTED 
                        filled_orders_in_tick.append(order)
                        filled_now = True

                elif order.side == OrderSide.SELL and order.price <= ask_price: # If limit price is met or better (higher)
                    execution_price = max(order.price, bid_price if bid_price is not None else current_price) # Execute at limit or better
                    if self.portfolio_manager.sell(timestamp, order.symbol, order.quantity, execution_price):
                        order.filled_quantity = order.quantity
                        order.filled_price = execution_price
                        order.status = OrderStatus.FILLED
                        filled_orders_in_tick.append(order)
                        filled_now = True
                        print(f"Limit Sell Order Filled: {order_id} at {execution_price}")
                    else:
                        # This case should ideally not happen if portfolio check is done before
                        order.status = OrderStatus.REJECTED
                        filled_orders_in_tick.append(order)
                        filled_now = True

            # Stop-Loss Order Logic
            elif order.order_type == OrderType.STOP_LOSS and order.status == OrderStatus.PENDING:
                if order.side == OrderSide.BUY and current_price <= order.stop_price:
                     # If price drops to or below stop_price, convert to market buy
                    print(f"Stop-Loss triggered for BUY order {order_id} at {current_price}. Converting to MARKET buy.")
                    order.order_type = OrderType.MARKET # Convert to market order
                    order.status = OrderStatus.PENDING # Re-process in the same tick
                    # This order will be processed again in the same tick with MARKET logic
                    continue # Skip adding to filled_orders_in_tick for now

                elif order.side == OrderSide.SELL and current_price >= order.stop_price:
                    # If price rises to or above stop_price, convert to market sell (this is often used as a take-profit, not stop-loss)
                    # For a true stop-loss on sell, it should trigger when price *falls* to stop price or below.
                    # Let's assume stop_price for SELL means trigger *at or below* this price.
                    # So, we need to check if current_price <= order.stop_price for SELL stop-loss
                    # If it's a true stop-loss for SELL: we're selling if price *falls* to stop_price or below.
                    # If it's a stop-limit for SELL: stop_price is the trigger, price is the execution limit.
                    # For simplicity, let's implement STOP_LOSS as Sell-at-Market when trigger price is hit.
                    # A more robust implementation would handle STOP_LIMIT separately.

                    # Re-evaluating STOP_LOSS logic:
                    # BUY STOP_LOSS: Buy at Market when current_price reaches or _exceeds_ stop_price (e.g., buy if price goes up).
                    # SELL STOP_LOSS: Sell at Market when current_price reaches or _falls below_ stop_price (e.g., sell to limit losses).

                    # Corrected SELL STOP_LOSS logic: trigger when current_price <= order.stop_price
                    if order.side == OrderSide.SELL and current_price <= order.stop_price:
                        print(f"Stop-Loss triggered for SELL order {order_id} at {current_price}. Converting to MARKET sell.")
                        order.order_type = OrderType.MARKET # Convert to market order
                        order.status = OrderStatus.PENDING # Re-process in the same tick
                        continue

                    # BUY STOP_LOSS logic: trigger when current_price >= order.stop_price
                    elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                        print(f"Stop-Loss triggered for BUY order {order_id} at {current_price}. Converting to MARKET buy.")
                        order.order_type = OrderType.MARKET # Convert to market order
                        order.status = OrderStatus.PENDING # Re-process in the same tick
                        continue


            # Remove orders that were fully filled or rejected in this tick
            if order.status in [OrderStatus.FILLED, OrderStatus.REJECTED]:
                if order_id in self.open_orders: # Ensure it hasn't been removed by a previous logic
                    del self.open_orders[order_id]

        return filled_orders_in_tick

    def cancel_order(self, order_id):
        if order_id in self.open_orders:
            order = self.open_orders[order_id]
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CANCELLED
                del self.open_orders[order_id]
                print(f"Order {order_id} cancelled.")
                return True
            else:
                print(f"Order {order_id} cannot be cancelled as it is already {order.status.value}.")
                return False
        else:
            print(f"Order {order_id} not found.")
            return False

    def get_open_orders_df(self):
        data = []
        for order_id, order in self.open_orders.items():
            data.append({
                'Order ID': order.order_id,
                'Symbol': order.symbol,
                'Type': order.order_type.value,
                'Side': order.side.value,
                'Quantity': order.quantity,
                'Price': order.price,
                'Stop Price': order.stop_price,
                'Status': order.status.value,
                'Filled Quantity': order.filled_quantity,
                'Timestamp': order.timestamp
            })
        return pd.DataFrame(data)


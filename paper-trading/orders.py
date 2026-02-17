from enum import Enum

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Order:
    def __init__(self, order_id, symbol, order_type, side, quantity, price=None, stop_price=None, timestamp=None):
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type # OrderType enum
        self.side = side         # OrderSide enum
        self.quantity = quantity
        self.price = price           # For LIMIT orders
        self.stop_price = stop_price   # For STOP_LOSS orders
        self.timestamp = timestamp
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0.0
        self.filled_price = 0.0 # Could be avg filled price

    def __str__(self):
        return (f"Order(id={self.order_id}, symbol={self.symbol}, type={self.order_type.value}, "
                f"side={self.side.value}, quantity={self.quantity}, price={self.price}, "
                f"stop_price={self.stop_price}, status={self.status.value}, "
                f"filled_quantity={self.filled_quantity})")

    def is_filled(self):
        return self.filled_quantity == self.quantity


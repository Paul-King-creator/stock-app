import React, { useState, useEffect } from 'react';

interface OrderBookProps {
  symbol: string;
}

interface OrderLevel {
  price: number;
  size: number;
  total: number;
}

const OrderBook: React.FC<OrderBookProps> = ({ symbol }) => {
  const [bids, setBids] = useState<OrderLevel[]>([]);
  const [asks, setAsks] = useState<OrderLevel[]>([]);
  const [spread, setSpread] = useState<number>(0);
  const [spreadPercent, setSpreadPercent] = useState<number>(0);

  useEffect(() => {
    // Simulate order book data
    // In a real app, this would come from a WebSocket or API
    const generateOrderBook = () => {
      fetch(`http://localhost:8000/stocks/${symbol}/history?limit=1`)
        .then(res => res.json())
        .then(data => {
          if (data.data && data.data.length > 0) {
            const midPrice = data.data[0].close;
            const newBids: OrderLevel[] = [];
            const newAsks: OrderLevel[] = [];
            
            let bidTotal = 0;
            let askTotal = 0;

            // Generate 10 levels for each side
            for (let i = 0; i < 10; i++) {
              const bidPrice = midPrice * (1 - (i + 1) * 0.001);
              const askPrice = midPrice * (1 + (i + 1) * 0.001);
              const bidSize = Math.floor(Math.random() * 1000) + 100;
              const askSize = Math.floor(Math.random() * 1000) + 100;
              
              bidTotal += bidSize;
              askTotal += askSize;

              newBids.push({ price: bidPrice, size: bidSize, total: bidTotal });
              newAsks.push({ price: askPrice, size: askSize, total: askTotal });
            }

            setBids(newBids);
            setAsks(newAsks);

            // Calculate spread
            const currentSpread = newAsks[0].price - newBids[0].price;
            setSpread(currentSpread);
            setSpreadPercent((currentSpread / midPrice) * 100);
          }
        })
        .catch(err => console.error('Error fetching order book:', err));
    };

    generateOrderBook();
    const interval = setInterval(generateOrderBook, 2000);

    return () => clearInterval(interval);
  }, [symbol]);

  const maxTotal = Math.max(
    bids.length > 0 ? bids[bids.length - 1].total : 0,
    asks.length > 0 ? asks[asks.length - 1].total : 0
  );

  return (
    <div className="order-book">
      <h3>Order Book</h3>
      
      <div className="spread-info">
        <span>Spread: ${spread.toFixed(2)} ({spreadPercent.toFixed(3)}%)</span>
      </div>

      <div className="order-book-grid">
        <div className="asks">
          <div className="header">
            <span>Price</span>
            <span>Size</span>
            <span>Total</span>
          </div>
          {[...asks].reverse().map((ask, i) => (
            <div key={i} className="order-row ask">
              <span className="price">${ask.price.toFixed(2)}</span>
              <span className="size">{ask.size}</span>
              <span className="total">{ask.total}</span>
              <div 
                className="depth-bar" 
                style={{ width: `${(ask.total / maxTotal) * 100}%` }}
              />
            </div>
          ))}
        </div>

        <div className="mid-price">
          {bids.length > 0 && asks.length > 0 && (
            <span>${((bids[0].price + asks[0].price) / 2).toFixed(2)}</span>
          )}
        </div>

        <div className="bids">
          {bids.map((bid, i) => (
            <div key={i} className="order-row bid">
              <span className="price">${bid.price.toFixed(2)}</span>
              <span className="size">{bid.size}</span>
              <span className="total">{bid.total}</span>
              <div 
                className="depth-bar" 
                style={{ width: `${(bid.total / maxTotal) * 100}%` }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OrderBook;

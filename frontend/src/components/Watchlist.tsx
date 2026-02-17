import React, { useState, useEffect } from 'react';

interface WatchlistProps {
  onSelectSymbol: (symbol: string) => void;
  selectedSymbol: string;
}

interface StockItem {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

const WATCHLIST_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META'];

const Watchlist: React.FC<WatchlistProps> = ({ onSelectSymbol, selectedSymbol }) => {
  const [stocks, setStocks] = useState<StockItem[]>([]);

  useEffect(() => {
    // Fetch all stocks in watchlist
    const fetchStocks = async () => {
      const stockPromises = WATCHLIST_SYMBOLS.map(symbol =>
        fetch(`http://localhost:8000/stocks/${symbol}/history?limit=2`)
          .then(res => res.json())
          .then(data => {
            if (data.data && data.data.length >= 2) {
              const latest = data.data[0];
              const prev = data.data[1];
              const change = latest.close - prev.close;
              const changePercent = (change / prev.close) * 100;
              return {
                symbol,
                price: latest.close,
                change,
                changePercent
              };
            }
            return null;
          })
          .catch(() => null)
      );

      const results = await Promise.all(stockPromises);
      setStocks(results.filter((s): s is StockItem => s !== null));
    };

    fetchStocks();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStocks, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="watchlist">
      <h3>Watchlist</h3>
      {stocks.map(stock => (
        <div
          key={stock.symbol}
          className={`watchlist-item ${stock.symbol === selectedSymbol ? 'active' : ''}`}
          onClick={() => onSelectSymbol(stock.symbol)}
        >
          <div>
            <div className="symbol">{stock.symbol}</div>
          </div>
          <div>
            <div className="price">${stock.price.toFixed(2)}</div>
            <div className={`change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
              {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Watchlist;

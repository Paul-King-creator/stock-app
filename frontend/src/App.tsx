import React, { useState, useEffect } from 'react';
import Chart from './components/Chart';
import Watchlist from './components/Watchlist';
import IndicatorPanel from './components/IndicatorPanel';
import OrderBook from './components/OrderBook';
import NewsFeed from './components/NewsFeed';
import Auth from './components/Auth';
import './App.css';

interface StockData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

interface User {
  id: string;
  username: string;
  email: string;
  portfolioValue: number;
  cash: number;
}

const App: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [showOrderBook, setShowOrderBook] = useState(false);
  const [showNews, setShowNews] = useState(false);

  const handleLogin = (loggedInUser: User) => {
    setUser(loggedInUser);
  };

  useEffect(() => {
    // Fetch initial stock data
    fetch(`http://localhost:8000/stocks/${selectedSymbol}/history?limit=1`)
      .then(res => res.json())
      .then(data => {
        if (data.data && data.data.length > 0) {
          const latest = data.data[0];
          const prev = data.data[1] || latest;
          const change = latest.close - prev.close;
          const changePercent = (change / prev.close) * 100;
          
          setStockData({
            symbol: selectedSymbol,
            price: latest.close,
            change: change,
            changePercent: changePercent
          });
        }
      })
      .catch(err => console.error('Error fetching stock data:', err));
  }, [selectedSymbol]);

  if (!user) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>Stock App</h1>
          <span className="user-info">Welcome, {user.username}</span>
        </div>
        <div className="header-right">
          <div className="portfolio-info">
            <span>Cash: ${user.cash.toLocaleString()}</span>
            <span>Portfolio: ${user.portfolioValue.toLocaleString()}</span>
          </div>
          <div className="stock-info">
            <span className="symbol">{selectedSymbol}</span>
            <span className="price">${stockData?.price.toFixed(2) || '--'}</span>
            <span className={`change ${(stockData?.change || 0) >= 0 ? 'positive' : 'negative'}`}>
              {(stockData?.change || 0) >= 0 ? '+' : ''}{(stockData?.change || 0).toFixed(2)} ({(stockData?.changePercent || 0).toFixed(2)}%)
            </span>
          </div>
        </div>
      </header>
      
      <main className="main">
        <aside className="sidebar">
          <Watchlist 
            onSelectSymbol={setSelectedSymbol} 
            selectedSymbol={selectedSymbol} 
          />
        </aside>
        
        <section className="content">
          <div className="chart-section">
            <Chart symbol={selectedSymbol} />
            <div className="toggle-buttons">
              <button 
                className={showOrderBook ? 'active' : ''} 
                onClick={() => setShowOrderBook(!showOrderBook)}
              >
                Order Book
              </button>
              <button 
                className={showNews ? 'active' : ''} 
                onClick={() => setShowNews(!showNews)}
              >
                News
              </button>
            </div>
            {showOrderBook && <OrderBook symbol={selectedSymbol} />}
            {showNews && <NewsFeed />}
          </div>
          <IndicatorPanel symbol={selectedSymbol} />
        </section>
      </main>
    </div>
  );
};

export default App;

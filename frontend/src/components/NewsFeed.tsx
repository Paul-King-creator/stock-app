import React, { useState, useEffect } from 'react';

interface NewsItem {
  id: string;
  title: string;
  source: string;
  timestamp: string;
  url: string;
  sentiment?: 'bullish' | 'bearish' | 'neutral';
}

// Mock news data - in production, this would come from a news API
const MOCK_NEWS: NewsItem[] = [
  {
    id: '1',
    title: 'AAPL Reports Strong Q4 Earnings, Beats Analyst Expectations',
    source: 'Reuters',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    url: '#',
    sentiment: 'bullish'
  },
  {
    id: '2',
    title: 'Federal Reserve Signals Potential Rate Cut in Coming Months',
    source: 'Bloomberg',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    url: '#',
    sentiment: 'bullish'
  },
  {
    id: '3',
    title: 'Tesla Faces Increased Competition in European EV Market',
    source: 'CNBC',
    timestamp: new Date(Date.now() - 10800000).toISOString(),
    url: '#',
    sentiment: 'bearish'
  },
  {
    id: '4',
    title: 'NVIDIA Announces New AI Chip, Stock Surges',
    source: 'TechCrunch',
    timestamp: new Date(Date.now() - 14400000).toISOString(),
    url: '#',
    sentiment: 'bullish'
  },
  {
    id: '5',
    title: 'Microsoft Cloud Revenue Growth Slows, Stock Dips',
    source: 'WSJ',
    timestamp: new Date(Date.now() - 18000000).toISOString(),
    url: '#',
    sentiment: 'bearish'
  },
  {
    id: '6',
    title: 'Market Overview: Tech Stocks Lead Recovery',
    source: 'MarketWatch',
    timestamp: new Date(Date.now() - 21600000).toISOString(),
    url: '#',
    sentiment: 'neutral'
  }
];

const NewsFeed: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>(MOCK_NEWS);
  const [filter, setFilter] = useState<string>('all');

  const filteredNews = filter === 'all' 
    ? news 
    : news.filter(item => item.sentiment === filter);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    
    if (hours < 1) {
      const minutes = Math.floor(diff / 60000);
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'bullish': return '#3fb950';
      case 'bearish': return '#f85149';
      default: return '#8b949e';
    }
  };

  return (
    <div className="news-feed">
      <div className="news-header">
        <h3>Market News</h3>
        <div className="news-filters">
          <button 
            className={filter === 'all' ? 'active' : ''} 
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={filter === 'bullish' ? 'active' : ''} 
            onClick={() => setFilter('bullish')}
          >
            Bullish
          </button>
          <button 
            className={filter === 'bearish' ? 'active' : ''} 
            onClick={() => setFilter('bearish')}
          >
            Bearish
          </button>
        </div>
      </div>

      <div className="news-list">
        {filteredNews.map(item => (
          <div key={item.id} className="news-item">
            <div className="news-meta">
              <span className="source">{item.source}</span>
              <span className="time">{formatTime(item.timestamp)}</span>
            </div>
            <a href={item.url} className="news-title">{item.title}</a>
            <div 
              className="sentiment-badge"
              style={{ backgroundColor: getSentimentColor(item.sentiment) }}
            >
              {item.sentiment}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NewsFeed;

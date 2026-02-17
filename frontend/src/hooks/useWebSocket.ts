import { useEffect, useState, useCallback } from 'react';

const WS_URL = 'ws://localhost:8765';

interface UseWebSocketOptions {
  url?: string;
  onMessage?: (data: any) => void;
}

interface UseWebSocketReturn {
  lastMessage: any | null;
  sendMessage: (data: any) => void;
  readyState: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const [lastMessage, setLastMessage] = useState<any | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);

  const { onMessage } = options;

  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setReadyState(WebSocket.OPEN);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
      if (onMessage) {
        onMessage(data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setReadyState(WebSocket.CLOSED);
    };

    return () => {
      ws.close();
    };
  }, [onMessage]);

  const sendMessage = useCallback((data: any) => {
    if (readyState === WebSocket.OPEN) {
      // WebSocket is open, send message
    }
  }, [readyState]);

  return { lastMessage, sendMessage, readyState };
};

// Custom hook for subscribing to a symbol
export const useSymbolSubscription = (symbol: string) => {
  const [price, setPrice] = useState<number | null>(null);
  const [bid, setBid] = useState<number | null>(null);
  const [ask, setAsk] = useState<number | null>(null);

  useEffect(() => {
    // In a real implementation, this would send a subscribe message to the WebSocket
    // For now, we'll simulate with polling
    const fetchQuote = () => {
      fetch(`http://100.83.241.57:8000/stocks/${symbol}/history?limit=1`)
        .then(res => res.json())
        .then(data => {
          if (data.data && data.data.length > 0) {
            setPrice(data.data[0].close);
          }
        })
        .catch(err => console.error('Error fetching quote:', err));
    };

    fetchQuote();
    const interval = setInterval(fetchQuote, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [symbol]);

  return { price, bid, ask };
};

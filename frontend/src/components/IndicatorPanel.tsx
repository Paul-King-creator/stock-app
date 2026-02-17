import React, { useState, useEffect } from 'react';

interface IndicatorPanelProps {
  symbol: string;
}

interface Indicators {
  sma?: number;
  ema?: number;
  rsi?: number;
  macd?: { line: number; signal: number; histogram: number };
}

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({ symbol }) => {
  const [indicators, setIndicators] = useState<Indicators>({});

  useEffect(() => {
    fetch(`http://localhost:8000/stocks/${symbol}/indicators?indicators=sma,rsi,macd,ema&window=20`)
      .then(res => res.json())
      .then(data => {
        const result: Indicators = {};
        
        if (data.sma && data.sma.length > 0) {
          result.sma = data.sma[data.sma.length - 1].value;
        }
        if (data.ema && data.ema.length > 0) {
          result.ema = data.ema[data.ema.length - 1].value;
        }
        if (data.rsi && data.rsi.length > 0) {
          result.rsi = data.rsi[data.rsi.length - 1].value;
        }
        if (data.macd && data.macd.line && data.macd.line.length > 0) {
          const lastIdx = data.macd.line.length - 1;
          result.macd = {
            line: data.macd.line[lastIdx].value,
            signal: data.macd.signal[lastIdx].value,
            histogram: data.macd.histogram[lastIdx].value
          };
        }
        
        setIndicators(result);
      })
      .catch(err => console.error('Error fetching indicators:', err));
  }, [symbol]);

  const getRSIColor = (rsi: number) => {
    if (rsi < 30) return '#3fb950'; // Oversold - bullish
    if (rsi > 70) return '#f85149'; // Overbought - bearish
    return '#c9d1d9';
  };

  return (
    <div className="indicator-panel">
      <h3>Technische Indikatoren</h3>
      <div className="indicator-grid">
        <div className="indicator-card">
          <div className="name">SMA 20</div>
          <div className="value">{indicators.sma?.toFixed(2) || '--'}</div>
        </div>
        <div className="indicator-card">
          <div className="name">EMA 20</div>
          <div className="value">{indicators.ema?.toFixed(2) || '--'}</div>
        </div>
        <div className="indicator-card">
          <div className="name">RSI 14</div>
          <div className="value" style={{ color: indicators.rsi ? getRSIColor(indicators.rsi) : '#c9d1d9' }}>
            {indicators.rsi?.toFixed(2) || '--'}
          </div>
        </div>
        <div className="indicator-card">
          <div className="name">MACD</div>
          <div className="value" style={{ fontSize: '0.9rem' }}>
            {indicators.macd ? (
              <>
                <div>Line: {indicators.macd.line.toFixed(4)}</div>
                <div>Signal: {indicators.macd.signal.toFixed(4)}</div>
                <div style={{ color: indicators.macd.histogram >= 0 ? '#3fb950' : '#f85149' }}>
                  Hist: {indicators.macd.histogram.toFixed(4)}
                </div>
              </>
            ) : '--'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndicatorPanel;

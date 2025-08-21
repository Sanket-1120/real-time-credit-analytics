import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const ExplanationChart = ({ explanation }) => {
  if (!explanation || !explanation.contributions) return null;
  const contributions = Object.entries(explanation.contributions)
    .map(([name, value]) => ({ name, value }))
    .filter(d => d.value !== 0)
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 7);
  return (
    <div className="card explanation-chart">
      <h3>Feature Contributions</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={contributions} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" name="Contribution" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
      <p className="base-value">Base Value (Avg. Prediction): {explanation.base_value}</p>
    </div>
  );
};

const RawDataTabs = ({ rawData }) => {
    const [activeTab, setActiveTab] = useState('news');
    if (!rawData) return null;
    return (
        <div className="card raw-data-card">
            <div className="tabs">
                <button onClick={() => setActiveTab('news')} className={activeTab === 'news' ? 'active' : ''}>Recent News</button>
                <button onClick={() => setActiveTab('macro')} className={activeTab === 'macro' ? 'active' : ''}>Macro Indicators</button>
            </div>
            <div className="tab-content">
                {activeTab === 'news' && rawData.news && (
                    <ul>
                        {rawData.news.slice(0, 10).map((item, index) => (
                            <li key={index}><a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a></li>
                        ))}
                    </ul>
                )}
                {activeTab === 'macro' && rawData.macro_data && (
                    <ul>
                        {Object.entries(rawData.macro_data).map(([key, value]) => (
                            <li key={key}><strong>{key}:</strong> {value}</li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

function App() {
  const [tickerInput, setTickerInput] = useState('AAPL,MSFT,GOOGL');
  const [currentTickers, setCurrentTickers] = useState('AAPL,MSFT,GOOGL');
  const [data, setData] = useState(null);
  const [history, setHistory] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // In App.jsx, replace your fetchData function with this one

  const fetchData = useCallback(async (tickers) => {
    if (!tickers) { setError('Please enter at least one ticker.'); return; }
    setLoading(true);
    setError('');
    
    const tickerList = tickers.split(',').map(t => t.trim().toUpperCase());
    const primaryTicker = tickerList[0];
    const backendUrl = 'https://real-time-credit-analytics.onrender.com';

    try {
      // --- THIS IS THE FIX ---
      // Added the missing '/data/' to the URL path
      const dataResponse = await axios.get(`${backendUrl}/data/${primaryTicker}`);
      // -----------------------
      
      setData(dataResponse.data);
      const historyResponse = await axios.get(`${backendUrl}/history/${tickers}`);
      setHistory(historyResponse.data);
    } catch (err) {
      setError('Failed to fetch data. Check tickers and backend.');
      console.error(err);
    }
    setLoading(false);
  }, []);
  
  useEffect(() => {
    fetchData(currentTickers);
  }, [currentTickers, fetchData]);

  const handleFetchClick = () => {
    setCurrentTickers(tickerInput);
  };

  const chartData = [];
  const colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#e64980"];
  if (Object.keys(history).length > 0) {
      const all_dates = new Set();
      Object.values(history).forEach(h => h.forEach(p => all_dates.add(p.date)));
      Array.from(all_dates).sort().forEach(date => {
          let dataPoint = { date };
          Object.keys(history).forEach(ticker => {
              const point = history[ticker].find(p => p.date === date);
              dataPoint[ticker] = point ? point.score : null;
          });
          chartData.push(dataPoint);
      });
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Real-Time Credit Intelligence</h1>
        <div className="search-bar">
          <input type="text" value={tickerInput} onChange={(e) => setTickerInput(e.target.value)} placeholder="Enter Tickers (e.g., AAPL,MSFT)" onKeyDown={(e) => e.key === 'Enter' && handleFetchClick()} />
          <button onClick={handleFetchClick} disabled={loading}>{loading ? 'Loading...' : 'Get Score'}</button>
        </div>
      </header>

      {loading && !data && <p className="loading-text">Loading initial data...</p>}
      {error && <p className="error">{error}</p>}
      
      {data && (
        <main className="dashboard-grid">
          <div className="card main-score">
            <h2>Score for {data.ticker}</h2>
            <div className="score-display">
                <span className="score">{data.credit_score.score}</span>
                <span className="score-out-of">/ 100</span>
            </div>
            {data.credit_score.alert && (<div className="alert">⚠️ {data.credit_score.alert}</div>)}
            {data.credit_score.key_headline && (
                <div className="key-event">
                    <h3>Key Driving Event</h3>
                    <p>{data.credit_score.key_headline}</p>
                </div>
            )}
          </div>
          
          <ExplanationChart explanation={data.credit_score.explanation} />
          
          <div className="card trend-chart">
              <h3>Score Trend Comparison</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }}/>
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  {Object.keys(history).map((ticker, index) => (
                    <Line key={ticker} type="monotone" dataKey={ticker} stroke={colors[index % colors.length]} strokeWidth={2} connectNulls />
                  ))}
                </LineChart>
              </ResponsiveContainer>
          </div>

          <RawDataTabs rawData={data.raw_data} />
        </main>
      )}
    </div>
  );
}

export default App;
// In: frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
// --- NEW RECHARTS IMPORTS ---
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [ticker, setTicker] = useState('AAPL');
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]); // State for historical data
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchData = async () => {
    if (!ticker) {
      setError('Please enter a ticker symbol.');
      return;
    }
    setLoading(true);
    setError('');
    setData(null);
    setHistory([]); // Clear previous history

    try {
      // Use Promise.all to fetch current data and history simultaneously
      const [dataResponse, historyResponse] = await Promise.all([
        axios.get(`http://127.0.0.1:8000/data/${ticker.toUpperCase()}`),
        axios.get(`http://127.0.0.1:8000/history/${ticker.toUpperCase()}`)
      ]);
      setData(dataResponse.data);
      setHistory(historyResponse.data);
    } catch (err) {
      setError('Failed to fetch data. Please check the ticker and if your backend is running.');
      console.error(err);
    }
    setLoading(false);
  };
  
  // Fetch data for the default ticker when the component first loads
  useEffect(() => {
    fetchData();
  }, []);


  return (
    <div className="container">
      <h1>Real-Time Credit Intelligence</h1>
      <div className="search-bar">
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="Enter Ticker (e.g., AAPL)"
        />
        <button onClick={fetchData} disabled={loading}>
          {loading ? 'Loading...' : 'Get Score'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      
      {data && (
        <div className="results">
          <div className="main-content">
            <div className="score-container">
              <h2>Score for {data.ticker}</h2>
              <div className="score-card">
                <span className="score">{data.credit_score.score}</span>
                <span className="score-out-of">/ 100</span>
              </div>
              <div className="explanation">
                <h3>Explanation:</h3>
                <ul>
                  {data.credit_score.explanation.map((line, index) => (
                    <li key={index}>{line}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* --- NEW TREND CHART --- */}
            <div className="chart-container">
              <h3>Score Trend (Last 30 Points)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={history} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="score" stroke="#8884d8" activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
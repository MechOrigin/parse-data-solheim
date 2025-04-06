import React, { useState, useEffect } from 'react';
import { Result } from '../types';
import '../styles/History.css';

interface HistoryProps {
  onSelectHistory: (history: Result[]) => void;
  onDeleteHistory: (id: string) => void;
}

export const History: React.FC<HistoryProps> = ({ onSelectHistory, onDeleteHistory }) => {
  const [history, setHistory] = useState<Result[]>([]);

  useEffect(() => {
    const loadHistory = () => {
      if (typeof window !== 'undefined') {
        const storedHistory = localStorage.getItem('acronymHistory');
        if (storedHistory) {
          try {
            const parsedHistory = JSON.parse(storedHistory);
            setHistory(parsedHistory);
          } catch (err) {
            console.error('Failed to parse history:', err);
          }
        }
      }
    };

    loadHistory();
  }, []);

  const handleSelect = (item: Result) => {
    onSelectHistory([item]);
  };

  const handleDelete = (id: string) => {
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);
    if (typeof window !== 'undefined') {
      localStorage.setItem('acronymHistory', JSON.stringify(updatedHistory));
    }
    onDeleteHistory(id);
  };

  return (
    <div className="history-container">
      <h2>History</h2>
      {history.length === 0 ? (
        <p>No history available</p>
      ) : (
        <ul className="history-list">
          {history.map((item) => (
            <li key={item.id} className="history-item">
              <div className="history-item-content">
                <span className="acronym">{item.acronym}</span>
                <span className="definition">{item.definition}</span>
              </div>
              <div className="history-item-actions">
                <button onClick={() => handleSelect(item)}>Select</button>
                <button onClick={() => handleDelete(item.id)}>Delete</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}; 
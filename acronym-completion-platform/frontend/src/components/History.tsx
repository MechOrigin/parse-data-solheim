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
      const storedHistory = localStorage.getItem('acronymHistory');
      if (storedHistory) {
        try {
          const parsedHistory = JSON.parse(storedHistory);
          setHistory(parsedHistory);
        } catch (err) {
          console.error('Error parsing history:', err);
        }
      }
    };

    loadHistory();
  }, []);

  const handleSelect = (item: Result) => {
    onSelectHistory([item]);
  };

  const handleDelete = (id: string) => {
    onDeleteHistory(id);
    setHistory(prev => prev.filter(item => item.id !== id));
    
    // Update localStorage
    const updatedHistory = history.filter(item => item.id !== id);
    localStorage.setItem('acronymHistory', JSON.stringify(updatedHistory));
  };

  return (
    <div className="history-container">
      <h2>History</h2>
      {history.length === 0 ? (
        <p className="no-history">No history items</p>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div key={item.id} className="history-item">
              <div className="history-content">
                <h3>{item.acronym}</h3>
                <p>{item.definition}</p>
                {item.description && <p className="description">{item.description}</p>}
                {item.tags.length > 0 && (
                  <div className="tags">
                    {item.tags.map((tag, index) => (
                      <span key={index} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
                <div className="metadata">
                  <span className="grade">Grade {item.grade}</span>
                  {Object.entries(item.metadata).map(([key, value]) => (
                    <span key={key} className="metadata-item">
                      {key}: {value}
                    </span>
                  ))}
                </div>
              </div>
              <div className="history-actions">
                <button
                  className="select-button"
                  onClick={() => handleSelect(item)}
                >
                  Select
                </button>
                <button
                  className="delete-button"
                  onClick={() => handleDelete(item.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}; 
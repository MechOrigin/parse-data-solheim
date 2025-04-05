import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { History } from '../components/History';

interface AcronymResult {
  acronym: string;
  definition: string;
  description: string;
  tags: string;
  grade: string;
}

interface HistoryItem {
  timestamp: string;
  acronymCount: number;
  results: AcronymResult[];
}

describe('History Component', () => {
  const mockOnSelectHistory = jest.fn();
  const mockOnDeleteHistory = jest.fn();
  const mockHistoryItem = {
    timestamp: '2024-04-05T12:00:00Z',
    acronymCount: 2,
    results: [
      {
        acronym: 'API',
        definition: 'Application Programming Interface',
        description: 'A set of rules and protocols for building software applications',
        tags: 'Programming,Software',
        grade: 'A'
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(Storage.prototype, 'getItem');
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders loading state initially', async () => {
    let resolvePromise: (value: string | null) => void;
    const promise = new Promise<string | null>(resolve => {
      resolvePromise = resolve;
    });

    // Mock localStorage to return data after a delay
    Storage.prototype.getItem = jest.fn(() => null);

    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    // Loading state should be visible initially
    expect(screen.getByText(/loading history/i)).toBeInTheDocument();

    // Resolve the promise to update the state
    act(() => {
      resolvePromise(JSON.stringify([mockHistoryItem]));
    });

    // Wait for the loading state to disappear
    expect(screen.queryByText(/loading history/i)).not.toBeInTheDocument();
  });

  it('renders no history message when empty', () => {
    // Mock localStorage to return null
    Storage.prototype.getItem = jest.fn(() => null);

    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    expect(screen.getByText('No history available')).toBeInTheDocument();
  });

  it('renders history items and handles interactions', () => {
    // Mock localStorage to return history items
    Storage.prototype.getItem = jest.fn(() => JSON.stringify([mockHistoryItem]));

    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    expect(screen.getByText('2 acronyms')).toBeInTheDocument();
    
    // Test load button
    const loadButton = screen.getByText('Load');
    fireEvent.click(loadButton);
    expect(mockOnSelectHistory).toHaveBeenCalledWith(mockHistoryItem.results);

    // Test delete button
    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);
    expect(mockOnDeleteHistory).toHaveBeenCalledWith(0);
  });

  it('handles localStorage error', () => {
    // Mock localStorage to throw an error
    Storage.prototype.getItem = jest.fn(() => {
      throw new Error('Storage error');
    });

    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    expect(screen.getByText('Error loading history')).toBeInTheDocument();
  });
}); 
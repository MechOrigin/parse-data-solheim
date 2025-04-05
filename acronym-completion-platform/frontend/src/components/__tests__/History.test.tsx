import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { History } from '../../components/History';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
    tr: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('tr', props, children),
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}));

describe('History Component', () => {
  const mockOnSelectHistory = jest.fn();
  const mockOnDeleteHistory = jest.fn();
  const mockHistory = [
    {
      timestamp: '2024-01-01T00:00:00.000Z',
      acronymCount: 2,
      results: [
        { acronym: 'ABC', definition: 'Test', description: 'Test', grade: 'A', tags: '' },
        { acronym: 'XYZ', definition: 'Test', description: 'Test', grade: 'B', tags: '' }
      ]
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    const mockLocalStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true
    });
  });

  it('renders empty state when no history is available', async () => {
    // Mock localStorage to return null
    (window.localStorage.getItem as jest.Mock).mockReturnValue(null);
    
    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    // Wait for loading state to finish
    await waitFor(() => {
      expect(screen.queryByText(/loading history/i)).not.toBeInTheDocument();
    });

    // Check for empty state message
    expect(screen.getByText(/no history available/i)).toBeInTheDocument();
  });

  it('renders history items when available', async () => {
    // Mock localStorage to return history data
    (window.localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(mockHistory));
    
    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    // Wait for loading state to finish and history items to be displayed
    await waitFor(() => {
      expect(screen.getByText(/2 acronyms/i)).toBeInTheDocument();
    });
  });

  it('handles invalid JSON from localStorage', async () => {
    // Mock localStorage to return invalid JSON
    (window.localStorage.getItem as jest.Mock).mockReturnValue('invalid json');
    
    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/error loading history/i)).toBeInTheDocument();
    });
  });

  it('calls onSelectHistory when Load button is clicked', async () => {
    // Mock localStorage to return history data
    (window.localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(mockHistory));
    
    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    // Wait for history items to be displayed
    await waitFor(() => {
      expect(screen.getByText(/2 acronyms/i)).toBeInTheDocument();
    });
    
    // Click the Load button
    const loadButton = screen.getByRole('button', { name: /load/i });
    fireEvent.click(loadButton);

    // Check if onSelectHistory was called with the correct data
    expect(mockOnSelectHistory).toHaveBeenCalledWith(mockHistory[0].results);
  });

  it('calls onDeleteHistory when Delete button is clicked', async () => {
    // Mock localStorage to return history data
    (window.localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(mockHistory));
    
    render(
      <History
        onSelectHistory={mockOnSelectHistory}
        onDeleteHistory={mockOnDeleteHistory}
      />
    );

    // Wait for history items to be displayed
    await waitFor(() => {
      expect(screen.getByText(/2 acronyms/i)).toBeInTheDocument();
    });
    
    // Click the Delete button
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    // Check if onDeleteHistory was called with the correct index
    expect(mockOnDeleteHistory).toHaveBeenCalledWith(0);
  });
}); 
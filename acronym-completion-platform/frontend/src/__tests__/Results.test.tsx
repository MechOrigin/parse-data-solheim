import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Results from '../components/Results';

interface Result {
  acronym: string;
  definition: string;
  description: string;
  tags: string[];
  grade: string;
}

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
    tr: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('tr', props, children),
  },
}));

// Mock the fetch function
global.fetch = jest.fn();

describe('Results Component', () => {
  const mockResults = [
    {
      acronym: 'API',
      definition: 'Application Programming Interface',
      description: 'A set of rules and protocols for building software applications',
      tags: ['Programming', 'Software'],
      grade: 'A'
    },
    {
      acronym: 'HTTP',
      definition: 'Hypertext Transfer Protocol',
      description: 'Protocol for transmitting web data',
      tags: ['Web', 'Protocol'],
      grade: 'B'
    }
  ];

  test('renders results table', () => {
    render(<Results results={mockResults} />);
    
    expect(screen.getByText('Results')).toBeInTheDocument();
    expect(screen.getByText('API')).toBeInTheDocument();
    expect(screen.getByText('Application Programming Interface')).toBeInTheDocument();
    expect(screen.getByText('A set of rules and protocols for building software applications')).toBeInTheDocument();
    expect(screen.getByText('Programming')).toBeInTheDocument();
    expect(screen.getByText('Software')).toBeInTheDocument();
    expect(screen.getByText('A')).toBeInTheDocument();

    expect(screen.getByText('HTTP')).toBeInTheDocument();
    expect(screen.getByText('Hypertext Transfer Protocol')).toBeInTheDocument();
    expect(screen.getByText('Protocol for transmitting web data')).toBeInTheDocument();
    expect(screen.getByText('Web')).toBeInTheDocument();
    expect(screen.getByText('Protocol')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
  });

  test('renders empty table when no results', () => {
    render(<Results results={[]} />);
    
    expect(screen.getByText('Results')).toBeInTheDocument();
    expect(screen.getByText('Acronym')).toBeInTheDocument();
    expect(screen.getByText('Definition')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Tags')).toBeInTheDocument();
    expect(screen.getByText('Grade')).toBeInTheDocument();
  });
}); 
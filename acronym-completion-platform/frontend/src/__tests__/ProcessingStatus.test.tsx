import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProcessingStatus from '../components/ProcessingStatus';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
    progress: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
  },
}));

describe('ProcessingStatus Component', () => {
  it('renders file status correctly', () => {
    const props = {
      templateFile: 'template.csv',
      acronymsFile: 'acronyms.csv',
      isProcessing: false,
      progress: 0,
      error: null,
    };

    render(<ProcessingStatus {...props} />);
    
    expect(screen.getByText('Template File:')).toBeInTheDocument();
    expect(screen.getByText('template.csv')).toBeInTheDocument();
    expect(screen.getByText('Acronyms File:')).toBeInTheDocument();
    expect(screen.getByText('acronyms.csv')).toBeInTheDocument();
  });

  it('shows pending status when files are not uploaded', () => {
    const props = {
      templateFile: null,
      acronymsFile: null,
      isProcessing: false,
      progress: 0,
      error: null,
    };

    render(<ProcessingStatus {...props} />);
    
    expect(screen.getAllByText('Not uploaded')).toHaveLength(2);
  });

  it('shows processing status and progress bar when processing', () => {
    const props = {
      templateFile: 'template.csv',
      acronymsFile: 'acronyms.csv',
      isProcessing: true,
      progress: 50,
      error: null,
    };

    render(<ProcessingStatus {...props} />);
    
    expect(screen.getByText('50%')).toBeInTheDocument();
    const progressFill = screen.getByRole('progressbar');
    expect(progressFill).toHaveAttribute('aria-valuenow', '50');
  });

  it('displays error message when there is an error', () => {
    const props = {
      templateFile: null,
      acronymsFile: null,
      isProcessing: false,
      progress: 0,
      error: 'Failed to process files',
    };

    render(<ProcessingStatus {...props} />);
    
    expect(screen.getByText('Failed to process files')).toBeInTheDocument();
  });
}); 
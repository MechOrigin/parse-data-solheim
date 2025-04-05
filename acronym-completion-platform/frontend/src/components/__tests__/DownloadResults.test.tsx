import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DownloadResults } from '../../components/DownloadResults';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
  },
}));

describe('DownloadResults Component', () => {
  const mockResults = [
    { acronym: 'ABC', definition: 'Test', description: 'Test', tags: '', grade: 'A' },
    { acronym: 'XYZ', definition: 'Test', description: 'Test', tags: '', grade: 'B' }
  ];

  beforeEach(() => {
    // Mock URL.createObjectURL and URL.revokeObjectURL
    window.URL.createObjectURL = jest.fn(() => 'blob:test');
    window.URL.revokeObjectURL = jest.fn();

    // Mock document.createElement to track created links
    const mockLink = {
      click: jest.fn(),
      setAttribute: jest.fn(),
      style: {},
      download: '',
      href: ''
    };
    document.createElement = jest.fn().mockReturnValue(mockLink);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders download button disabled when no results', () => {
    const { container } = render(<DownloadResults results={[]} />);
    
    const downloadButton = screen.getByRole('button', { name: /download results/i });
    expect(downloadButton).toBeDisabled();
  });

  it('renders download button enabled with results count', () => {
    const { container } = render(<DownloadResults results={mockResults} />);
    
    const downloadButton = screen.getByRole('button', { name: /download results \(2 acronyms\)/i });
    expect(downloadButton).toBeEnabled();
  });

  it('triggers download with default filename when clicked', () => {
    const { container } = render(<DownloadResults results={mockResults} />);
    
    const downloadButton = screen.getByRole('button', { name: /download results/i });
    fireEvent.click(downloadButton);

    const mockLink = document.createElement('a');
    expect(mockLink.download).toBe('acronyms.csv');
    expect(mockLink.click).toHaveBeenCalled();
    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(window.URL.revokeObjectURL).toHaveBeenCalled();
  });

  it('uses custom filename when provided', () => {
    const { container } = render(<DownloadResults results={mockResults} filename="custom.csv" />);
    
    const downloadButton = screen.getByRole('button', { name: /download results/i });
    fireEvent.click(downloadButton);

    const mockLink = document.createElement('a');
    expect(mockLink.download).toBe('custom.csv');
    expect(mockLink.click).toHaveBeenCalled();
    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(window.URL.revokeObjectURL).toHaveBeenCalled();
  });
}); 
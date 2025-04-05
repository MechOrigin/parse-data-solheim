import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DownloadResults } from '../components/DownloadResults';

describe('DownloadResults Component', () => {
  beforeEach(() => {
    // Mock URL.createObjectURL
    URL.createObjectURL = jest.fn(() => 'mock-url');
    // Mock document.createElement
    document.createElement = jest.fn().mockImplementation((tagName) => ({
      setAttribute: jest.fn(),
      style: {},
      click: jest.fn(),
    }));
    // Mock document.body.appendChild and removeChild
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders download button with correct text', () => {
    const mockResults = [
      {
        acronym: 'API',
        definition: 'Application Programming Interface',
        description: 'A set of rules and protocols',
        tags: 'Programming',
        grade: 'A'
      }
    ];

    render(<DownloadResults results={mockResults} />);
    expect(screen.getByText(/Download Results \(1 acronyms?\)/)).toBeInTheDocument();
  });

  it('disables button when no results are provided', () => {
    render(<DownloadResults results={[]} />);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('creates and triggers download when button is clicked', async () => {
    const mockResults = [
      {
        acronym: 'API',
        definition: 'Application Programming Interface',
        description: 'A set of rules and protocols',
        tags: 'Programming',
        grade: 'A'
      }
    ];

    render(<DownloadResults results={mockResults} />);
    const button = screen.getByRole('button');
    
    await act(async () => {
      fireEvent.click(button);
    });

    expect(document.createElement).toHaveBeenCalledWith('a');
    expect(document.body.appendChild).toHaveBeenCalled();
    expect(document.body.removeChild).toHaveBeenCalled();
  });

  it('uses custom filename when provided', async () => {
    const mockResults = [
      {
        acronym: 'API',
        definition: 'Application Programming Interface',
        description: 'A set of rules and protocols',
        tags: 'Programming',
        grade: 'A'
      }
    ];

    render(<DownloadResults results={mockResults} filename="custom.csv" />);
    const button = screen.getByRole('button');
    
    await act(async () => {
      fireEvent.click(button);
    });

    const link = (document.createElement as jest.Mock).mock.results[0].value;
    expect(link.setAttribute).toHaveBeenCalledWith('download', 'custom.csv');
  });
}); 
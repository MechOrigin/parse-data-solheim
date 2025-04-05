import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    h1: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('h1', props, children),
    button: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('button', props, children),
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
    tr: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('tr', props, children),
  },
}));

// Mock window.alert
global.window.alert = jest.fn();

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock successful health check by default
    mockFetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'healthy' })
      })
    );
  });

  test('renders app title and components', () => {
    render(<App />);
    
    expect(screen.getByText('Acronym Completion Platform')).toBeInTheDocument();
    expect(screen.getByText('Template File')).toBeInTheDocument();
    expect(screen.getByText('Acronyms File')).toBeInTheDocument();
  });

  test('handles file uploads correctly', () => {
    render(<App />);
    
    const templateInput = screen.getByTestId('file-upload-template-file');
    const acronymsInput = screen.getByTestId('file-upload-acronyms-file');
    
    const templateFile = new File(['template content'], 'template.csv', { type: 'text/csv' });
    const acronymsFile = new File(['acronyms content'], 'acronyms.csv', { type: 'text/csv' });
    
    fireEvent.change(templateInput, { target: { files: [templateFile] } });
    fireEvent.change(acronymsInput, { target: { files: [acronymsFile] } });
    
    // Check file names in the file upload components
    const fileNames = screen.getAllByTestId('file-name');
    expect(fileNames[0]).toHaveTextContent('template.csv');
    expect(fileNames[1]).toHaveTextContent('acronyms.csv');
  });

  test('handles settings changes', () => {
    render(<App />);
    
    const temperatureInput = screen.getByLabelText('Temperature:');
    const maxTokensInput = screen.getByLabelText('Max Tokens:');
    
    fireEvent.change(temperatureInput, { target: { value: '0.8' } });
    fireEvent.change(maxTokensInput, { target: { value: '1500' } });
    
    expect(temperatureInput).toHaveValue(0.8);
    expect(maxTokensInput).toHaveValue(1500);
  });

  test('enables process button when files are uploaded', () => {
    render(<App />);
    
    const templateInput = screen.getByTestId('file-upload-template-file');
    const acronymsInput = screen.getByTestId('file-upload-acronyms-file');
    
    const templateFile = new File(['template content'], 'template.csv', { type: 'text/csv' });
    const acronymsFile = new File(['acronyms content'], 'acronyms.csv', { type: 'text/csv' });
    
    fireEvent.change(templateInput, { target: { files: [templateFile] } });
    fireEvent.change(acronymsInput, { target: { files: [acronymsFile] } });
    
    const processButton = screen.getByText('Process Acronyms');
    expect(processButton).toBeEnabled();
  });

  test('processes acronyms when files are uploaded', async () => {
    const mockResults = [
      {
        acronym: 'API',
        definition: 'Application Programming Interface',
        description: 'A set of rules and protocols for building software applications',
        tags: ['Web', 'Protocol'],
        grade: 'A'
      }
    ];

    mockFetch
      .mockImplementationOnce(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'healthy' }) }))
      .mockImplementationOnce(() => Promise.resolve({ ok: true }))
      .mockImplementationOnce(() => Promise.resolve({ ok: true }))
      .mockImplementationOnce(() => Promise.resolve({ 
        ok: true, 
        json: () => Promise.resolve({ results: mockResults }) 
      }));

    render(<App />);
    
    const templateFile = new File(['template content'], 'template.csv', { type: 'text/csv' });
    const acronymsFile = new File(['acronyms content'], 'acronyms.csv', { type: 'text/csv' });
    
    const templateInput = screen.getByTestId('file-upload-template-file');
    const acronymsInput = screen.getByTestId('file-upload-acronyms-file');
    
    fireEvent.change(templateInput, { target: { files: [templateFile] } });
    fireEvent.change(acronymsInput, { target: { files: [acronymsFile] } });
    
    const processButton = screen.getByText('Process Acronyms');
    fireEvent.click(processButton);
    
    await waitFor(() => {
      expect(screen.getByText('API')).toBeInTheDocument();
      expect(screen.getByText('Application Programming Interface')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('displays error when processing fails', async () => {
    mockFetch
      .mockImplementationOnce(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'healthy' }) }))
      .mockImplementationOnce(() => Promise.resolve({ ok: true }))
      .mockImplementationOnce(() => Promise.resolve({ ok: true }))
      .mockImplementationOnce(() => Promise.resolve({ 
        ok: false, 
        json: () => Promise.resolve({ detail: 'Failed to process acronyms' }) 
      }));

    render(<App />);
    
    const templateFile = new File(['template content'], 'template.csv', { type: 'text/csv' });
    const acronymsFile = new File(['acronyms content'], 'acronyms.csv', { type: 'text/csv' });
    
    const templateInput = screen.getByTestId('file-upload-template-file');
    const acronymsInput = screen.getByTestId('file-upload-acronyms-file');
    
    fireEvent.change(templateInput, { target: { files: [templateFile] } });
    fireEvent.change(acronymsInput, { target: { files: [acronymsFile] } });
    
    const processButton = screen.getByText('Process Acronyms');
    fireEvent.click(processButton);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to process acronyms')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('displays error when backend is not available', async () => {
    mockFetch.mockImplementation(() => Promise.reject(new Error('Network error')));

    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText('Cannot connect to backend service')).toBeInTheDocument();
    });
  });
}); 
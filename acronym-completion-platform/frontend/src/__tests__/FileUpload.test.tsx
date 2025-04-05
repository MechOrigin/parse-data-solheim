import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FileUpload } from '../components/FileUpload';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
  },
}));

describe('FileUpload Component', () => {
  const mockOnFileUpload = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders with the correct label', () => {
    render(<FileUpload label="Template CSV" onFileUpload={mockOnFileUpload} />);
    expect(screen.getByText('Template CSV')).toBeInTheDocument();
  });
  
  it('calls onFileUpload when a file is selected', () => {
    render(<FileUpload label="Template CSV" onFileUpload={mockOnFileUpload} />);
    
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByLabelText('Template CSV');
    
    fireEvent.change(input, { target: { files: [file] } });
    
    expect(mockOnFileUpload).toHaveBeenCalledWith(file);
  });
  
  it('displays the file name when a file is provided', () => {
    const fileName = 'test.csv';
    render(
      <FileUpload
        label="Template CSV"
        onFileUpload={mockOnFileUpload}
        fileName={fileName}
      />
    );
    
    expect(screen.getByText(fileName)).toBeInTheDocument();
  });
  
  it('does not display the file name when no file is provided', () => {
    render(<FileUpload label="Template CSV" onFileUpload={mockOnFileUpload} />);
    
    const fileNameElement = screen.queryByText(/\.csv$/);
    expect(fileNameElement).not.toBeInTheDocument();
  });
  
  it('handles invalid file type', () => {
    render(<FileUpload label="Template CSV" onFileUpload={mockOnFileUpload} />);
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText('Template CSV');
    
    fireEvent.change(input, { target: { files: [file] } });
    
    expect(mockOnFileUpload).not.toHaveBeenCalled();
    expect(screen.getByText('Please upload a CSV file')).toBeInTheDocument();
  });
  
  it('clears error message when a valid file is selected after an error', () => {
    render(<FileUpload label="Template CSV" onFileUpload={mockOnFileUpload} />);
    
    // First, upload an invalid file
    const invalidFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText('Template CSV');
    
    fireEvent.change(input, { target: { files: [invalidFile] } });
    expect(screen.getByText('Please upload a CSV file')).toBeInTheDocument();
    
    // Then, upload a valid file
    const validFile = new File(['test content'], 'test.csv', { type: 'text/csv' });
    fireEvent.change(input, { target: { files: [validFile] } });
    
    expect(screen.queryByText('Please upload a CSV file')).not.toBeInTheDocument();
    expect(mockOnFileUpload).toHaveBeenCalledWith(validFile);
  });
}); 
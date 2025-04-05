import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { FileUpload } from '../../components/FileUpload';

describe('FileUpload Component', () => {
  const mockOnFileUpload = jest.fn();
  const mockFile = new File(['test content'], 'test.csv', { type: 'text/csv' });
  const label = 'Choose File';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders file input and upload button', () => {
    render(<FileUpload label={label} onFileUpload={mockOnFileUpload} />);
    
    expect(screen.getByLabelText(label)).toBeInTheDocument();
    expect(screen.getByText(/click or drag and drop a csv file/i)).toBeInTheDocument();
  });

  it('enables file upload when file is selected', async () => {
    render(<FileUpload label={label} onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(label);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(mockOnFileUpload).toHaveBeenCalledWith(mockFile);
    });
  });

  it('shows error message for invalid file type', async () => {
    render(<FileUpload label={label} onFileUpload={mockOnFileUpload} />);
    
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    const fileInput = screen.getByLabelText(label);
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    await waitFor(() => {
      expect(screen.getByText(/please upload a csv file/i)).toBeInTheDocument();
      expect(mockOnFileUpload).not.toHaveBeenCalled();
    });
  });

  it('shows file name when provided', () => {
    const fileName = 'test.csv';
    render(<FileUpload label={label} onFileUpload={mockOnFileUpload} fileName={fileName} />);

    expect(screen.getByTestId('file-name')).toHaveTextContent(fileName);
  });

  it('handles drag and drop', async () => {
    render(<FileUpload label={label} onFileUpload={mockOnFileUpload} />);
    
    const dropZone = screen.getByText(/click or drag and drop a csv file/i).parentElement!;
    fireEvent.drop(dropZone, { 
      dataTransfer: { files: [mockFile] }
    });

    await waitFor(() => {
      expect(mockOnFileUpload).toHaveBeenCalledWith(mockFile);
    });
  });
}); 
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Settings from '../components/Settings';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
  },
}));

describe('Settings Component', () => {
  const mockOnSettingsChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders settings form', () => {
    render(<Settings onSettingsChange={mockOnSettingsChange} />);
    
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Temperature/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Max Tokens/i)).toBeInTheDocument();
  });

  test('updates temperature setting', () => {
    render(<Settings onSettingsChange={mockOnSettingsChange} />);
    
    const temperatureInput = screen.getByLabelText(/Temperature/i);
    fireEvent.change(temperatureInput, { target: { value: '0.8' } });
    
    expect(mockOnSettingsChange).toHaveBeenCalledWith({
      temperature: 0.8,
      maxTokens: 1000
    });
  });

  test('updates max tokens setting', () => {
    render(<Settings onSettingsChange={mockOnSettingsChange} />);
    
    const maxTokensInput = screen.getByLabelText(/Max Tokens/i);
    fireEvent.change(maxTokensInput, { target: { value: '2000' } });
    
    expect(mockOnSettingsChange).toHaveBeenCalledWith({
      temperature: 0.7,
      maxTokens: 2000
    });
  });

  test('validates temperature input', () => {
    render(<Settings onSettingsChange={mockOnSettingsChange} />);
    
    const temperatureInput = screen.getByLabelText(/Temperature/i);
    
    // Test value below range
    fireEvent.change(temperatureInput, { target: { value: '-0.1' } });
    expect(screen.getByText(/Temperature must be between 0 and 1/i)).toBeInTheDocument();
    expect(mockOnSettingsChange).not.toHaveBeenCalled();
    
    // Test value above range
    fireEvent.change(temperatureInput, { target: { value: '1.1' } });
    expect(screen.getByText(/Temperature must be between 0 and 1/i)).toBeInTheDocument();
    expect(mockOnSettingsChange).not.toHaveBeenCalled();
    
    // Test valid value
    fireEvent.change(temperatureInput, { target: { value: '0.5' } });
    expect(screen.queryByText(/Temperature must be between 0 and 1/i)).not.toBeInTheDocument();
    expect(mockOnSettingsChange).toHaveBeenCalledWith({ temperature: 0.5, maxTokens: 1000 });
  });

  test('validates max tokens input', () => {
    render(<Settings onSettingsChange={mockOnSettingsChange} />);
    
    const maxTokensInput = screen.getByLabelText(/Max Tokens/i);
    
    // Test value below range
    fireEvent.change(maxTokensInput, { target: { value: '0' } });
    expect(screen.getByText(/Max tokens must be between 1 and 2000/i)).toBeInTheDocument();
    expect(mockOnSettingsChange).not.toHaveBeenCalled();
    
    // Test value above range
    fireEvent.change(maxTokensInput, { target: { value: '2001' } });
    expect(screen.getByText(/Max tokens must be between 1 and 2000/i)).toBeInTheDocument();
    expect(mockOnSettingsChange).not.toHaveBeenCalled();
    
    // Test valid value
    fireEvent.change(maxTokensInput, { target: { value: '500' } });
    expect(screen.queryByText(/Max tokens must be between 1 and 2000/i)).not.toBeInTheDocument();
    expect(mockOnSettingsChange).toHaveBeenCalledWith({ temperature: 0.7, maxTokens: 500 });
  });
}); 
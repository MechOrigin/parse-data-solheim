import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { EditAcronym } from '../../components/EditAcronym';

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
    p: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('p', props, children),
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}));

describe('EditAcronym Component', () => {
  const mockOnSave = jest.fn();
  const mockOnCancel = jest.fn();
  const mockAcronym = {
    acronym: 'ABC',
    definition: 'Test Definition',
    description: 'Test Description',
    tags: 'tag1,tag2',
    grade: '3'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form with initial values', () => {
    render(
      <EditAcronym 
        acronym={mockAcronym} 
        onSave={mockOnSave} 
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByLabelText(/acronym/i)).toHaveValue('ABC');
    expect(screen.getByLabelText(/definition/i)).toHaveValue('Test Definition');
    expect(screen.getByLabelText(/description/i)).toHaveValue('Test Description');
    expect(screen.getByLabelText(/tags/i)).toHaveValue('tag1,tag2');
    expect(screen.getByLabelText(/grade/i)).toHaveValue('3');
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(
      <EditAcronym 
        acronym={mockAcronym} 
        onSave={mockOnSave} 
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('calls onSave with updated values when form is submitted', async () => {
    render(
      <EditAcronym 
        acronym={mockAcronym} 
        onSave={mockOnSave} 
        onCancel={mockOnCancel}
      />
    );

    // Update form fields
    fireEvent.change(screen.getByLabelText(/definition/i), {
      target: { value: 'New Definition', name: 'definition' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'New Description', name: 'description' }
    });
    fireEvent.change(screen.getByLabelText(/tags/i), {
      target: { value: 'newtag1,newtag2', name: 'tags' }
    });
    fireEvent.change(screen.getByLabelText(/grade/i), {
      target: { value: '4', name: 'grade' }
    });

    // Submit form
    const form = screen.getByRole('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledWith({
        ...mockAcronym,
        definition: 'New Definition',
        description: 'New Description',
        tags: 'newtag1,newtag2',
        grade: '4'
      });
    });
  });

  it('shows validation errors when required fields are empty', async () => {
    render(
      <EditAcronym 
        acronym={mockAcronym} 
        onSave={mockOnSave} 
        onCancel={mockOnCancel}
      />
    );

    // Clear required fields
    fireEvent.change(screen.getByLabelText(/definition/i), {
      target: { value: '', name: 'definition' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: '', name: 'description' }
    });
    fireEvent.change(screen.getByLabelText(/grade/i), {
      target: { value: '', name: 'grade' }
    });

    // Submit form
    const form = screen.getByRole('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/definition is required/i)).toBeInTheDocument();
      expect(screen.getByText(/description is required/i)).toBeInTheDocument();
      expect(screen.getByText(/grade must be between 1 and 5/i)).toBeInTheDocument();
      expect(mockOnSave).not.toHaveBeenCalled();
    });
  });

  it('clears validation errors when fields are filled', async () => {
    render(
      <EditAcronym 
        acronym={mockAcronym} 
        onSave={mockOnSave} 
        onCancel={mockOnCancel}
      />
    );

    // Clear required field
    fireEvent.change(screen.getByLabelText(/definition/i), {
      target: { value: '', name: 'definition' }
    });

    // Submit form to show error
    const form = screen.getByRole('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/definition is required/i)).toBeInTheDocument();
    });

    // Fill the field
    fireEvent.change(screen.getByLabelText(/definition/i), {
      target: { value: 'New Definition', name: 'definition' }
    });

    await waitFor(() => {
      expect(screen.queryByText(/definition is required/i)).not.toBeInTheDocument();
    });
  });
}); 
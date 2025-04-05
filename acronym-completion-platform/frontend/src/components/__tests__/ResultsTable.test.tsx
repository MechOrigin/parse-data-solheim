import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ResultsTable } from '../../components/ResultsTable';

// Mock EditAcronym component
jest.mock('../../components/EditAcronym', () => ({
  EditAcronym: ({ acronym, onSave, onCancel }: any) => (
    <div data-testid="edit-acronym-form">
      <input type="text" value={acronym.acronym} readOnly />
      <input type="text" value={acronym.definition} readOnly />
      <input type="text" value={acronym.tags} readOnly />
      <button onClick={() => onSave(acronym)}>Save Changes</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  )
}));

// Mock framer-motion to avoid animation-related issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('div', props, children),
    tr: ({ children, ...props }: { children: React.ReactNode; [key: string]: any }) => React.createElement('tr', props, children),
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}));

describe('ResultsTable Component', () => {
  const mockOnResultsChange = jest.fn();
  const mockResults = [
    { acronym: 'ABC', definition: 'Test', description: 'Test', tags: 'tag1,tag2', grade: 'A' },
    { acronym: 'XYZ', definition: 'Test', description: 'Test', tags: 'tag3,tag4', grade: 'B' },
    { acronym: 'DEF', definition: 'Test', description: 'Test', tags: 'tag5,tag6', grade: 'C' }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders table with all results', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    expect(screen.getByText('ABC')).toBeInTheDocument();
    expect(screen.getByText('XYZ')).toBeInTheDocument();
    expect(screen.getByText('DEF')).toBeInTheDocument();
  });

  it('displays correct definitions and descriptions', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    const cells = screen.getAllByRole('cell');
    const definitionCells = cells.filter((cell, index) => index % 6 === 1); // Definition is the second column
    const descriptionCells = cells.filter((cell, index) => index % 6 === 2); // Description is the third column

    definitionCells.forEach(cell => {
      expect(cell).toHaveTextContent('Test');
    });
    descriptionCells.forEach(cell => {
      expect(cell).toHaveTextContent('Test');
    });
  });

  it('filters results by grade', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Select grade A
    const gradeFilter = screen.getByLabelText('Filter by Grade');
    fireEvent.change(gradeFilter, { target: { value: 'A' } });

    const rows = screen.getAllByRole('row').slice(1); // Skip header row
    expect(rows).toHaveLength(1);
    expect(within(rows[0]).getByText('ABC')).toBeInTheDocument();
    expect(within(rows[0]).getByText('A')).toBeInTheDocument();
  });

  it('filters results by search term', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Search for XYZ
    const searchInput = screen.getByPlaceholderText('Search acronyms, definitions, etc.');
    fireEvent.change(searchInput, { target: { value: 'XYZ' } });

    const rows = screen.getAllByRole('row').slice(1); // Skip header row
    expect(rows).toHaveLength(1);
    expect(within(rows[0]).getByText('XYZ')).toBeInTheDocument();
    
    const cells = within(rows[0]).getAllByRole('cell');
    expect(cells[1]).toHaveTextContent('Test'); // Definition
    expect(cells[2]).toHaveTextContent('Test'); // Description
  });

  it('sorts results by acronym', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Click the Acronym header twice to sort in ascending order
    const acronymHeader = screen.getByText('Acronym');
    fireEvent.click(acronymHeader);
    fireEvent.click(acronymHeader);

    // Get all rows
    const rows = screen.getAllByRole('row').slice(1); // Skip header row
    const acronyms = rows.map(row => within(row).getAllByRole('cell')[0].textContent);

    // Should be sorted alphabetically
    expect(acronyms).toEqual(['ABC', 'DEF', 'XYZ']);
  });

  it('sorts results by grade', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Click the Grade header to sort
    const gradeHeader = screen.getByText('Grade');
    fireEvent.click(gradeHeader);

    // Get all grade cells
    const rows = screen.getAllByRole('row').slice(1); // Skip header row
    const grades = rows.map(row => within(row).getAllByRole('cell')[4].textContent);

    // Should be sorted alphabetically
    expect(grades).toEqual(['A', 'B', 'C']);
  });

  it('displays edit button for each row', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    const editButtons = screen.getAllByText('Edit');
    expect(editButtons).toHaveLength(3);
  });

  it('shows edit form when edit button is clicked', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Click edit button for first row
    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    // Verify edit form is shown
    expect(screen.getByTestId('edit-acronym-form')).toBeInTheDocument();
    expect(screen.getByDisplayValue('ABC')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test')).toBeInTheDocument();
    expect(screen.getByDisplayValue('tag1,tag2')).toBeInTheDocument();
  });

  it('displays "No results found" when filtered results are empty', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    const searchInput = screen.getByPlaceholderText('Search acronyms, definitions, etc.');
    fireEvent.change(searchInput, { target: { value: 'NonexistentTerm' } });

    expect(screen.getByText('No results found')).toBeInTheDocument();
  });

  it('filters results by tags', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Search for tag1
    const searchInput = screen.getByPlaceholderText('Search acronyms, definitions, etc.');
    fireEvent.change(searchInput, { target: { value: 'tag1' } });

    const rows = screen.getAllByRole('row').slice(1); // Skip header row
    expect(rows).toHaveLength(1);
    expect(within(rows[0]).getByText('ABC')).toBeInTheDocument();
    expect(within(rows[0]).getByText('tag1,tag2')).toBeInTheDocument();
  });

  it('calls onResultsChange when editing is saved', () => {
    render(<ResultsTable results={mockResults} onResultsChange={mockOnResultsChange} />);

    // Click edit button for first row
    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);

    // Click save button
    fireEvent.click(screen.getByText('Save Changes'));

    // Verify onResultsChange was called with updated results
    expect(mockOnResultsChange).toHaveBeenCalledWith(expect.arrayContaining([
      expect.objectContaining({ acronym: 'ABC' })
    ]));
  });
}); 
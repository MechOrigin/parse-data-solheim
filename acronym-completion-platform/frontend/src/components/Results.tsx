import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { InlineEditAcronym } from './InlineEditAcronym';
import { Result } from '../types';
import '../styles/Results.css';

interface ResultsProps {
  results: Result[];
  onUpdateAcronym?: (result: Result) => void;
}

type SortField = 'acronym' | 'definition' | 'grade';
type SortDirection = 'asc' | 'desc';

const Results: React.FC<ResultsProps> = ({ results, onUpdateAcronym }) => {
  const [selectedGrades, setSelectedGrades] = useState<string[]>([]);
  const [sortField, setSortField] = useState<SortField>('acronym');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const [editingAcronym, setEditingAcronym] = useState<string | null>(null);

  // Get unique grades from results
  const availableGrades = useMemo(() => {
    const grades = new Set(results.map(result => result.grade));
    return Array.from(grades).sort();
  }, [results]);

  // Filter and sort results
  const filteredAndSortedResults = useMemo(() => {
    let filtered = results;

    // Apply grade filter
    if (selectedGrades.length > 0) {
      filtered = filtered.filter(result => selectedGrades.includes(result.grade));
    }

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(result =>
        result.acronym.toLowerCase().includes(term) ||
        result.definition.toLowerCase().includes(term) ||
        result.description.toLowerCase().includes(term)
      );
    }

    // Apply sorting
    return [...filtered].sort((a, b) => {
      const aValue = a[sortField].toLowerCase();
      const bValue = b[sortField].toLowerCase();
      return sortDirection === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    });
  }, [results, selectedGrades, sortField, sortDirection, searchTerm]);

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const toggleGrade = (grade: string) => {
    setSelectedGrades(prev =>
      prev.includes(grade)
        ? prev.filter(g => g !== grade)
        : [...prev, grade]
    );
  };

  const handleEdit = (acronym: string) => {
    setEditingAcronym(acronym);
  };

  const handleSave = (updatedAcronym: Result) => {
    if (onUpdateAcronym) {
      onUpdateAcronym(updatedAcronym);
    }
    setEditingAcronym(null);
  };

  const handleCancel = () => {
    setEditingAcronym(null);
  };

  const handleUpdate = (result: Result) => {
    if (onUpdateAcronym) {
      onUpdateAcronym(result);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="results-container"
    >
      <div className="results-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search acronyms..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="grade-filters">
          <span className="filter-label">Filter by Grade:</span>
          <div className="grade-buttons">
            {availableGrades.map(grade => (
              <button
                key={grade}
                onClick={() => toggleGrade(grade)}
                className={`grade-filter-btn ${selectedGrades.includes(grade) ? 'active' : ''}`}
              >
                {grade}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="results-table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('acronym')} className="sortable">
                Acronym {sortField === 'acronym' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('definition')} className="sortable">
                Definition {sortField === 'definition' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Description</th>
              <th>Tags</th>
              <th onClick={() => handleSort('grade')} className="sortable">
                Grade {sortField === 'grade' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {filteredAndSortedResults.map((result, index) => (
                editingAcronym === result.acronym ? (
                  <InlineEditAcronym
                    key={`edit-${result.acronym}`}
                    acronym={result}
                    onSave={handleSave}
                    onCancel={handleCancel}
                  />
                ) : (
                  <motion.tr
                    key={result.acronym}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <td>{result.acronym}</td>
                    <td>{result.definition}</td>
                    <td>{result.description}</td>
                    <td>
                      <div className="tags-container">
                        {result.tags.map((tag, tagIndex) => (
                          <span key={tagIndex} className="tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <span className={`grade grade-${result.grade.toLowerCase()}`}>
                        {result.grade}
                      </span>
                    </td>
                    <td>
                      <span className={`status-indicator ${result.isEnriched ? 'enriched' : 'pending'}`}>
                        {result.isEnriched ? '✓' : '⋯'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => handleEdit(result.acronym)}
                        className="edit-button"
                        title="Edit"
                      >
                        ✎
                      </button>
                    </td>
                  </motion.tr>
                )
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default Results; 
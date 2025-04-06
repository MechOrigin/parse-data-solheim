import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { InlineEditAcronym } from './InlineEditAcronym';
import { Result } from '../types';
import '../styles/Results.css';

interface Acronym {
  acronym: string;
  definition: string;
  description: string;
  tags: string[];
  grade: string;
  isEnriched?: boolean;
}

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
    const grades = new Set(results.map(result => result.grade.toString()));
    return Array.from(grades).sort((a, b) => Number(a) - Number(b));
  }, [results]);

  // Filter and sort results
  const filteredAndSortedResults = useMemo(() => {
    let filtered = results;

    // Apply grade filter
    if (selectedGrades.length > 0) {
      filtered = filtered.filter(result => selectedGrades.includes(result.grade.toString()));
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
      if (sortField === 'grade') {
        return sortDirection === 'asc' ? a.grade - b.grade : b.grade - a.grade;
      }
      const aValue = a[sortField].toString().toLowerCase();
      const bValue = b[sortField].toString().toLowerCase();
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    });
  }, [results, selectedGrades, searchTerm, sortField, sortDirection]);

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

  const handleSave = (updatedAcronym: Acronym) => {
    if (onUpdateAcronym) {
      const result: Result = {
        id: crypto.randomUUID(),
        acronym: updatedAcronym.acronym,
        definition: updatedAcronym.definition,
        description: updatedAcronym.description,
        tags: updatedAcronym.tags,
        grade: Number(updatedAcronym.grade),
        metadata: {}
      };
      onUpdateAcronym(result);
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
    <div className="results-container">
      <div className="results-header">
        <div className="results-filters">
          <div className="grade-filter">
            <label>Filter by Grade:</label>
            <div className="grade-buttons">
              {availableGrades.map(grade => (
                <button
                  key={grade}
                  className={`grade-button ${selectedGrades.includes(grade) ? 'selected' : ''}`}
                  onClick={() => toggleGrade(grade)}
                >
                  {grade}
                </button>
              ))}
            </div>
          </div>
          <div className="search-filter">
            <input
              type="text"
              placeholder="Search acronyms..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="results-sort">
          <button
            className={`sort-button ${sortField === 'acronym' ? 'active' : ''}`}
            onClick={() => handleSort('acronym')}
          >
            Acronym {sortField === 'acronym' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button
            className={`sort-button ${sortField === 'definition' ? 'active' : ''}`}
            onClick={() => handleSort('definition')}
          >
            Definition {sortField === 'definition' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
          <button
            className={`sort-button ${sortField === 'grade' ? 'active' : ''}`}
            onClick={() => handleSort('grade')}
          >
            Grade {sortField === 'grade' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
        </div>
      </div>
      <div className="results-list">
        <AnimatePresence>
          {filteredAndSortedResults.map((result) => (
            <motion.div
              key={result.id}
              className="result-item"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {editingAcronym === result.acronym ? (
                <InlineEditAcronym
                  acronym={{
                    acronym: result.acronym,
                    definition: result.definition,
                    description: result.description,
                    tags: result.tags,
                    grade: result.grade.toString()
                  }}
                  onSave={handleSave}
                  onCancel={handleCancel}
                />
              ) : (
                <div className="result-content">
                  <div className="result-header">
                    <h3>{result.acronym}</h3>
                    <span className="grade-badge">Grade {result.grade}</span>
                  </div>
                  <p className="definition">{result.definition}</p>
                  <p className="description">{result.description}</p>
                  <div className="tags">
                    {result.tags.map((tag, index) => (
                      <span key={index} className="tag">{tag}</span>
                    ))}
                  </div>
                  <div className="result-actions">
                    <button onClick={() => handleEdit(result.acronym)}>Edit</button>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Results; 
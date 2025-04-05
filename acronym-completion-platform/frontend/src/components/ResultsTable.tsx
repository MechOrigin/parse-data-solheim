import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { EditAcronym } from './EditAcronym';

interface Result {
  acronym: string;
  definition: string;
  description: string;
  tags: string;
  grade: string;
}

interface ResultsTableProps {
  results: Result[];
  onResultsChange: (updatedResults: Result[]) => void;
}

export function ResultsTable({ results, onResultsChange }: ResultsTableProps) {
  const [filteredGrade, setFilteredGrade] = useState<string>('all');
  const [sortField, setSortField] = useState<keyof Result>('acronym');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [editingAcronym, setEditingAcronym] = useState<Result | null>(null);

  // Apply filters and sorting
  const filteredAndSortedResults = useMemo(() => {
    // First, filter by grade
    let filtered = [...results];
    if (filteredGrade !== 'all') {
      filtered = filtered.filter(result => result.grade === filteredGrade);
    }

    // Then, filter by search term
    if (searchTerm) {
      const searchTermLower = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(result => {
        // Check for exact matches in acronym, definition, description
        if (result.acronym.toLowerCase() === searchTermLower) return true;
        if (result.definition.toLowerCase() === searchTermLower) return true;
        if (result.description.toLowerCase() === searchTermLower) return true;
        
        // Check for exact matches in tags
        const tags = result.tags.toLowerCase().split(',').map(tag => tag.trim());
        return tags.some(tag => tag === searchTermLower);
      });
    }

    // Finally, sort the results
    return [...filtered].sort((a, b) => {
      if (sortField === 'grade') {
        const aNum = parseInt(a.grade, 10);
        const bNum = parseInt(b.grade, 10);
        return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
      }
      
      const aValue = a[sortField].toLowerCase();
      const bValue = b[sortField].toLowerCase();
      const comparison = aValue.localeCompare(bValue);
      return sortDirection === 'desc' ? -comparison : comparison;
    });
  }, [results, filteredGrade, searchTerm, sortField, sortDirection]);

  // Handle filter change
  const handleFilterChange = (value: string) => {
    setFilteredGrade(value);
  };

  // Handle search change
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
  };

  // Handle sort change
  const handleSort = (field: keyof Result) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Handle edit
  const handleEdit = (acronym: Result) => {
    setEditingAcronym(acronym);
  };

  // Handle save
  const handleSave = (updatedAcronym: Result) => {
    const updatedResults = results.map(result => 
      result.acronym === updatedAcronym.acronym ? updatedAcronym : result
    );
    onResultsChange(updatedResults);
    setEditingAcronym(null);
  };

  // Handle cancel
  const handleCancel = () => {
    setEditingAcronym(null);
  };

  // Get unique grades for filter dropdown
  const uniqueGrades = Array.from(new Set(results.map(r => r.grade))).sort();

  return (
    <div className="space-y-6">
      {editingAcronym ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <EditAcronym
            acronym={editingAcronym}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="search"
                  value={searchTerm}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  placeholder="Search acronyms, definitions, etc."
                  className="input-field pl-10"
                />
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
            </div>
            
            <div className="w-full md:w-48">
              <label htmlFor="grade-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Grade
              </label>
              <select
                id="grade-filter"
                value={filteredGrade}
                onChange={(e) => handleFilterChange(e.target.value)}
                className="input-field"
              >
                <option value="all">All Grades</option>
                {uniqueGrades.map(grade => (
                  <option key={grade} value={grade}>Grade {grade}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {['acronym', 'definition', 'description', 'tags', 'grade'].map((field) => (
                      <th
                        key={field}
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors duration-200"
                        onClick={() => handleSort(field as keyof Result)}
                      >
                        <div className="flex items-center space-x-1">
                          <span>{field.charAt(0).toUpperCase() + field.slice(1)}</span>
                          {sortField === field && (
                            <svg
                              className={`h-4 w-4 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`}
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path
                                fillRule="evenodd"
                                d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                clipRule="evenodd"
                              />
                            </svg>
                          )}
                        </div>
                      </th>
                    ))}
                    <th scope="col" className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredAndSortedResults.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                        No results found
                      </td>
                    </tr>
                  ) : (
                    filteredAndSortedResults.map((result, index) => (
                      <motion.tr
                        key={result.acronym}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="hover:bg-gray-50 transition-colors duration-200"
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {result.acronym}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {result.definition}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          <div className="max-w-xs truncate">
                            {result.description}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {result.tags}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" data-testid="grade-cell">
                          {result.grade}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleEdit(result)}
                            className="text-primary-600 hover:text-primary-900 transition-colors duration-200"
                          >
                            Edit
                          </button>
                        </td>
                      </motion.tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
} 
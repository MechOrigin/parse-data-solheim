import { useState } from 'react';
import { motion } from 'framer-motion';

interface Acronym {
  acronym: string;
  definition: string;
  description: string;
  tags: string;
  grade: string;
}

interface EditAcronymProps {
  acronym: Acronym;
  onSave: (updatedAcronym: Acronym) => void;
  onCancel: () => void;
}

export function EditAcronym({ acronym, onSave, onCancel }: EditAcronymProps) {
  const [editedAcronym, setEditedAcronym] = useState<Acronym>({ ...acronym });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setEditedAcronym(prev => ({ ...prev, [name]: value }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!editedAcronym.acronym.trim()) {
      newErrors.acronym = 'Acronym is required';
    }
    
    if (!editedAcronym.definition.trim()) {
      newErrors.definition = 'Definition is required';
    }
    
    if (!editedAcronym.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (!editedAcronym.grade || !['1', '2', '3', '4', '5'].includes(editedAcronym.grade)) {
      newErrors.grade = 'Grade must be between 1 and 5';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSave(editedAcronym);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="glass-panel p-6 sm:p-8"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Edit Acronym</h3>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-500 transition-colors duration-200"
        >
          <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6" role="form">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="acronym" className="block text-sm font-medium text-gray-700 mb-1">
              Acronym
            </label>
            <input
              type="text"
              id="acronym"
              name="acronym"
              value={editedAcronym.acronym}
              onChange={handleChange}
              className={`input-field ${errors.acronym ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : ''}`}
            />
            {errors.acronym && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-sm text-red-600"
              >
                {errors.acronym}
              </motion.p>
            )}
          </div>
          
          <div>
            <label htmlFor="definition" className="block text-sm font-medium text-gray-700 mb-1">
              Definition
            </label>
            <input
              type="text"
              id="definition"
              name="definition"
              value={editedAcronym.definition}
              onChange={handleChange}
              className={`input-field ${errors.definition ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : ''}`}
            />
            {errors.definition && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-sm text-red-600"
              >
                {errors.definition}
              </motion.p>
            )}
          </div>
        </div>
        
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            rows={3}
            value={editedAcronym.description}
            onChange={handleChange}
            className={`input-field ${errors.description ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : ''}`}
          />
          {errors.description && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600"
            >
              {errors.description}
            </motion.p>
          )}
        </div>
        
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
              Tags
            </label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={editedAcronym.tags}
              onChange={handleChange}
              placeholder="Comma-separated tags"
              className="input-field"
            />
          </div>
          
          <div>
            <label htmlFor="grade" className="block text-sm font-medium text-gray-700 mb-1">
              Grade
            </label>
            <select
              id="grade"
              name="grade"
              value={editedAcronym.grade}
              onChange={handleChange}
              className={`input-field ${errors.grade ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : ''}`}
            >
              <option value="">Select a grade</option>
              {[1, 2, 3, 4, 5].map(grade => (
                <option key={grade} value={grade.toString()}>
                  Grade {grade}
                </option>
              ))}
            </select>
            {errors.grade && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-sm text-red-600"
              >
                {errors.grade}
              </motion.p>
            )}
          </div>
        </div>
        
        <div className="flex justify-end space-x-4 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
          >
            Save Changes
          </button>
        </div>
      </form>
    </motion.div>
  );
} 
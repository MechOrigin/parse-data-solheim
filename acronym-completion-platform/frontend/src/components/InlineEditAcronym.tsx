import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface Acronym {
  acronym: string;
  definition: string;
  description: string;
  tags: string[];
  grade: string;
  isEnriched?: boolean;
}

interface InlineEditAcronymProps {
  acronym: Acronym;
  onSave: (updatedAcronym: Acronym) => void;
  onCancel: () => void;
}

export const InlineEditAcronym: React.FC<InlineEditAcronymProps> = ({
  acronym,
  onSave,
  onCancel,
}) => {
  const [editedAcronym, setEditedAcronym] = useState<Acronym>({ ...acronym });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const acronymInputRef = useRef<HTMLInputElement>(null);

  // Focus the acronym input when the component mounts
  useEffect(() => {
    if (acronymInputRef.current) {
      acronymInputRef.current.focus();
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Handle tags as an array
    if (name === 'tags') {
      const tagArray = value.split(',').map(tag => tag.trim()).filter(tag => tag);
      setEditedAcronym(prev => ({ ...prev, [name]: tagArray }));
    } else {
      setEditedAcronym(prev => ({ ...prev, [name]: value }));
    }
    
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
      newErrors.acronym = 'Required';
    }
    
    if (!editedAcronym.definition.trim()) {
      newErrors.definition = 'Required';
    }
    
    if (!editedAcronym.description.trim()) {
      newErrors.description = 'Required';
    }
    
    if (!editedAcronym.grade || !['1', '2', '3', '4', '5'].includes(editedAcronym.grade)) {
      newErrors.grade = 'Invalid';
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <motion.tr
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="inline-edit-row"
    >
      <td>
        <input
          ref={acronymInputRef}
          type="text"
          name="acronym"
          value={editedAcronym.acronym}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          className={`inline-edit-input ${errors.acronym ? 'error' : ''}`}
        />
        {errors.acronym && <span className="error-message">{errors.acronym}</span>}
      </td>
      <td>
        <input
          type="text"
          name="definition"
          value={editedAcronym.definition}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          className={`inline-edit-input ${errors.definition ? 'error' : ''}`}
        />
        {errors.definition && <span className="error-message">{errors.definition}</span>}
      </td>
      <td>
        <textarea
          name="description"
          value={editedAcronym.description}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          className={`inline-edit-textarea ${errors.description ? 'error' : ''}`}
          rows={2}
        />
        {errors.description && <span className="error-message">{errors.description}</span>}
      </td>
      <td>
        <input
          type="text"
          name="tags"
          value={editedAcronym.tags.join(', ')}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Comma-separated tags"
          className="inline-edit-input"
        />
      </td>
      <td>
        <select
          name="grade"
          value={editedAcronym.grade}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          className={`inline-edit-select ${errors.grade ? 'error' : ''}`}
        >
          {[1, 2, 3, 4, 5].map(grade => (
            <option key={grade} value={grade.toString()}>
              {grade}
            </option>
          ))}
        </select>
        {errors.grade && <span className="error-message">{errors.grade}</span>}
      </td>
      <td>
        <div className="inline-edit-actions">
          <button
            type="button"
            onClick={handleSubmit}
            className="save-button"
            title="Save"
          >
            ✓
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="cancel-button"
            title="Cancel"
          >
            ✕
          </button>
        </div>
      </td>
    </motion.tr>
  );
}; 
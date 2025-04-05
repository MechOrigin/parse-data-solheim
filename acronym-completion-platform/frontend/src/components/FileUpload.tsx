import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import '../styles/FileUpload.css';

interface FileUploadProps {
  label: string;
  onFileUpload: (file: File) => void;
  fileName?: string | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({ label, onFileUpload, fileName }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.csv')) {
        setError('Please upload a CSV file');
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setError(null);
      onFileUpload(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.csv')) {
        setError('Please upload a CSV file');
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setError(null);
      onFileUpload(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="file-upload-container"
      onClick={handleClick}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".csv"
        style={{ display: 'none' }}
        id={`file-upload-${label.toLowerCase().replace(/\s+/g, '-')}`}
        aria-label={label}
        data-testid={`file-upload-${label.toLowerCase().replace(/\s+/g, '-')}`}
        role="file"
      />
      
      <div className="file-upload-content">
        <div className="file-upload-icon">📁</div>
        <div className="file-upload-text">
          {fileName ? (
            <span className="file-name" data-testid="file-name">{fileName}</span>
          ) : (
            <>
              <span className="upload-label">{label}</span>
              <span className="upload-instruction">Click or drag and drop a CSV file</span>
            </>
          )}
        </div>
      </div>
      {error && (
        <div className="text-red-500 text-sm mt-2" data-testid="error-message">
          {error}
        </div>
      )}
    </motion.div>
  );
}; 
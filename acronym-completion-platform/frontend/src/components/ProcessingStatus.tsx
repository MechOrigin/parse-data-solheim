import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/ProcessingStatus.css';

interface ProcessingStatusProps {
  templateFile: string | null;
  acronymsFile: string | null;
  isProcessing: boolean;
  progress: number;
  error: string | null;
}

type ProcessingStep = 'idle' | 'uploading' | 'parsing' | 'enriching' | 'completing';

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  templateFile,
  acronymsFile,
  isProcessing,
  progress,
  error,
}) => {
  const [currentStep, setCurrentStep] = useState<string>('Initializing');
  const [statusMessage, setStatusMessage] = useState<string>('');

  useEffect(() => {
    if (isProcessing) {
      if (progress === 0) {
        setCurrentStep('Initializing');
        setStatusMessage('Setting up processing...');
      } else if (progress < 25) {
        setCurrentStep('Processing');
        setStatusMessage('Starting acronym processing...');
      } else if (progress < 50) {
        setCurrentStep('Processing');
        setStatusMessage('Processing acronyms...');
      } else if (progress < 75) {
        setCurrentStep('Processing');
        setStatusMessage('Continuing acronym processing...');
      } else if (progress < 100) {
        setCurrentStep('Finalizing');
        setStatusMessage('Finalizing results...');
      } else {
        setCurrentStep('Complete');
        setStatusMessage('Processing complete!');
      }
    }
  }, [isProcessing, progress]);

  useEffect(() => {
    if (error) {
      if (error.includes('API key issues')) {
        setCurrentStep('Error');
        setStatusMessage('API key issues detected. Please check your API keys.');
      } else if (error.includes('quota has been exhausted')) {
        setCurrentStep('Error');
        setStatusMessage('API quota exhausted. Please try again later.');
      } else {
        setCurrentStep('Error');
        setStatusMessage(error);
      }
    }
  }, [error]);

  const steps: { id: ProcessingStep; label: string }[] = [
    { id: 'uploading', label: 'Upload' },
    { id: 'parsing', label: 'Parse' },
    { id: 'enriching', label: 'Enrich' },
    { id: 'completing', label: 'Complete' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="processing-status-container"
    >
      <div className="status-content">
        <div className="status-header">
          <h3>Processing Status</h3>
          <span className={`status-indicator ${isProcessing ? 'processing' : error ? 'error' : 'complete'}`}>
            {currentStep}
          </span>
        </div>
        
        <div className="file-status">
          <div className="status-item">
            <span className="status-label">Template File:</span>
            <span className={`status-value ${templateFile ? 'success' : 'pending'}`}>
              {templateFile || 'Not uploaded'}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Acronyms File:</span>
            <span className={`status-value ${acronymsFile ? 'success' : 'pending'}`}>
              {acronymsFile || 'Not uploaded'}
            </span>
          </div>
        </div>

        {isProcessing && (
          <>
            <div className="progress-steps">
              {steps.map((step, index) => (
                <div key={step.id} className="step-container">
                  <div 
                    className={`step-indicator ${
                      currentStep === step.id 
                        ? 'active' 
                        : steps.findIndex(s => s.id === currentStep) > index 
                          ? 'completed' 
                          : ''
                    }`}
                  >
                    {steps.findIndex(s => s.id === currentStep) > index ? (
                      <svg className="check-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    ) : (
                      <span>{index + 1}</span>
                    )}
                  </div>
                  <span className="step-label">{step.label}</span>
                </div>
              ))}
            </div>
            <div className="progress-bar-container">
              <div 
                className="progress-bar" 
                style={{ width: `${progress}%` }}
              />
              <span className="progress-text">{Math.round(progress)}%</span>
            </div>
          </>
        )}

        <div className={`status-message ${error ? 'error' : ''}`}>
          {statusMessage}
        </div>
      </div>
    </motion.div>
  );
};

export default ProcessingStatus; 
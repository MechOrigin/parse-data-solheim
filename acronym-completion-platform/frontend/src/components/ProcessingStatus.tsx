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
  const [currentStep, setCurrentStep] = useState<ProcessingStep>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');

  // Update the current step and status message based on progress
  useEffect(() => {
    if (!isProcessing) {
      setCurrentStep('idle');
      setStatusMessage('');
      return;
    }

    if (progress < 20) {
      setCurrentStep('uploading');
      setStatusMessage('Uploading and validating files...');
    } else if (progress < 40) {
      setCurrentStep('parsing');
      setStatusMessage('Parsing acronyms from files...');
    } else if (progress < 80) {
      setCurrentStep('enriching');
      setStatusMessage('Enriching acronyms with AI models...');
    } else {
      setCurrentStep('completing');
      setStatusMessage('Finalizing results...');
    }
  }, [isProcessing, progress]);

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
                  {index < steps.length - 1 && (
                    <div 
                      className={`step-connector ${
                        steps.findIndex(s => s.id === currentStep) > index ? 'completed' : ''
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>

            <div className="progress-container">
              <div className="progress-bar">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                  role="progressbar"
                  aria-valuenow={progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
              <div className="progress-details">
                <span className="progress-text">{progress}%</span>
                <AnimatePresence mode="wait">
                  <motion.span
                    key={statusMessage}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }}
                    className="status-message"
                  >
                    {statusMessage}
                  </motion.span>
                </AnimatePresence>
              </div>
            </div>
          </>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="error-message"
          >
            {error}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default ProcessingStatus; 
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileUpload } from './components/FileUpload';
import Settings from './components/Settings';
import ProcessingStatus from './components/ProcessingStatus';
import Results from './components/Results';
import { History } from './components/History';
import { ThemeProvider } from './components/ThemeProvider';
import { SettingsState, Result, FileUploadProps, ProcessingStatusProps, ResultsProps, HistoryProps } from './types';
import './styles/App.css';

const App: React.FC = () => {
  const [settings, setSettings] = useState<SettingsState>({
    temperature: 0.7,
    maxTokens: 1000,
    model: 'grok',
    batchSize: 10,
    autoSave: true,
    historyLimit: 50,
    theme: 'system',
    gradeFilter: {
      enabled: false,
      min: 1,
      max: 5
    },
    selectiveEnrichment: false,
    enrichment: {
      enabled: true,
      addMissingDefinitions: true,
      generateDescriptions: true,
      suggestTags: true,
      useWebSearch: false,
      useInternalKb: true
    },
    rateLimiting: {
      enabled: true,
      requestsPerSecond: 0.5,
      burstSize: 1,
      maxRetries: 3
    },
    outputFormat: {
      includeDefinitions: true,
      includeDescriptions: true,
      includeTags: true,
      includeGrade: true,
      includeMetadata: false
    },
    caching: {
      enabled: true,
      ttlSeconds: 86400
    }
  });

  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [acronymsFile, setAcronymsFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [showHistory, setShowHistory] = useState<boolean>(false);

  useEffect(() => {
    // Check backend health on startup
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => {
        if (data.status !== 'healthy') {
          setError('Backend service is not healthy');
        }
      })
      .catch(() => {
        setError('Cannot connect to backend service');
      });
  }, []);

  const handleSettingsChange = (newSettings: SettingsState) => {
    setSettings(newSettings);
    
    // Update backend configuration
    fetch('http://localhost:8000/update-config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newSettings),
    }).catch(err => {
      console.error('Failed to update settings:', err);
    });
  };

  const handleTemplateUpload = async (file: File) => {
    setTemplateFile(file);
    setError(null);
    
    // Upload template file to backend
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/upload-template', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload template file');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while uploading template file');
    }
  };

  const handleAcronymsUpload = async (file: File) => {
    setAcronymsFile(file);
    setError(null);
    
    // Upload acronyms file to backend
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/upload-acronyms', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload acronyms file');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while uploading acronyms file');
    }
  };

  const processAcronyms = async () => {
    if (!templateFile || !acronymsFile) {
      setError('Please upload both template and acronyms files');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('template', templateFile);
      formData.append('acronyms', acronymsFile);
      formData.append('settings', JSON.stringify(settings));

      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process acronyms');
      }

      const data = await response.json();
      const processedResults: Result[] = data.results.map((result: any) => ({
        id: result.id || crypto.randomUUID(),
        acronym: result.acronym,
        definition: result.definition,
        description: result.description || '',
        tags: result.tags || [],
        grade: result.grade || 1,
        metadata: result.metadata || {}
      }));

      setResults(processedResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsProcessing(false);
      setProgress(100);
    }
  };

  const handleUpdateAcronym = (result: Result) => {
    setResults(prevResults => 
      prevResults.map(r => r.id === result.id ? result : r)
    );
  };

  const saveToHistory = (results: Result[]) => {
    try {
      // Get existing history
      const storedHistory = localStorage.getItem('acronymHistory');
      const history = storedHistory ? JSON.parse(storedHistory) : [];
      
      // Create new history item
      const newHistoryItem = {
        timestamp: new Date().toISOString(),
        acronymCount: results.length,
        results: results.map(result => ({
          ...result,
          tags: result.tags.join(', ') // Convert tags array to string for storage
        }))
      };
      
      // Add to history (limit to 10 items)
      const updatedHistory = [newHistoryItem, ...history].slice(0, 10);
      
      // Save to localStorage
      localStorage.setItem('acronymHistory', JSON.stringify(updatedHistory));
      
      // Show success message
      setError('Results saved to history');
      setTimeout(() => setError(null), 3000);
    } catch (err) {
      console.error('Error saving to history:', err);
    }
  };

  const handleSelectHistory = (history: Result[]) => {
    setResults(history);
  };

  const handleDeleteHistory = (id: string) => {
    setResults(prevResults => prevResults.filter(r => r.id !== id));
  };

  const downloadResults = async () => {
    try {
      const response = await fetch('http://localhost:8000/download-results');
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to download results');
      }
      
      // Create a blob from the response
      const blob = await response.blob();
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(blob);
      
      // Create a temporary link element
      const a = document.createElement('a');
      a.href = url;
      a.download = 'results.csv';
      
      // Append the link to the body
      document.body.appendChild(a);
      
      // Click the link
      a.click();
      
      // Remove the link
      document.body.removeChild(a);
      
      // Revoke the URL
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while downloading results');
    }
  };

  return (
    <ThemeProvider>
      <div className="app-container">
        <header className="app-header">
          <h1>Acronym Completion Platform</h1>
        </header>
        <main className="app-main">
          <Settings onSettingsChange={handleSettingsChange} />
          <div className="content-section">
            <FileUpload 
              label="Template File"
              onFileUpload={handleTemplateUpload}
              fileName={templateFile?.name || null}
            />
            <FileUpload 
              label="Acronyms File"
              onFileUpload={handleAcronymsUpload}
              fileName={acronymsFile?.name || null}
            />
            <ProcessingStatus 
              templateFile={templateFile?.name || null}
              acronymsFile={acronymsFile?.name || null}
              isProcessing={isProcessing}
              progress={progress}
              error={error}
            />
            <Results 
              results={results}
              onUpdateAcronym={handleUpdateAcronym}
            />
            <History 
              onSelectHistory={handleSelectHistory}
              onDeleteHistory={handleDeleteHistory}
            />
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
};

export default App; 
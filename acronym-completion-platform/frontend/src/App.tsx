import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileUpload } from './components/FileUpload';
import Settings from './components/Settings';
import ProcessingStatus from './components/ProcessingStatus';
import Results from './components/Results';
import { History } from './components/History';
import { ThemeProvider } from './components/ThemeProvider';
import { SettingsState, Result, FileUploadProps, ProcessingStatusProps, ResultsProps, HistoryProps } from './types';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import './styles/App.css';

const AppContent: React.FC = () => {
  const { token, isAuthenticated, login } = useAuth();
  const [settings, setSettings] = useState<SettingsState>({
    geminiApiKeys: [''],
    batchSize: 25,
    gradeFilter: {
      enabled: false,
      singleGrade: null,
      gradeRange: null
    },
    enrichment: {
      enabled: true,
      addMissingDefinitions: true,
      generateDescriptions: true
    },
    model: 'gemini',
    autoSave: true,
    historyLimit: 50,
    theme: 'system'
  });

  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [acronymsFile, setAcronymsFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [showHistory, setShowHistory] = useState<boolean>(false);

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  });

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
      headers: getAuthHeaders(),
      body: JSON.stringify(newSettings),
    }).catch(err => {
      console.error('Failed to update settings:', err);
    });
  };

  const handleTemplateUpload = async (file: File) => {
    setTemplateFile(file);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/upload-template', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload template file');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleAcronymsUpload = async (file: File) => {
    setAcronymsFile(file);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/upload-acronyms', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload acronyms file');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const processAcronyms = async () => {
    try {
      setIsProcessing(true);
      setError(null);
      setProgress(0);
      setResults([]);

      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process acronyms');
      }

      const data = await response.json();
      
      // Check for API key issues or quota exhaustion
      const apiKeyIssue = data.results.find((r: any) => r.acronym === 'API_KEY_ISSUES');
      const quotaExhausted = data.results.find((r: any) => r.acronym === 'QUOTA_EXHAUSTED');
      
      if (apiKeyIssue) {
        setError('API key issues detected. Some acronyms may not have been processed correctly. Please check your API keys.');
        // Filter out the API_KEY_ISSUES entry from results
        data.results = data.results.filter((r: any) => r.acronym !== 'API_KEY_ISSUES');
      } else if (quotaExhausted) {
        setError('API quota has been exhausted. Some acronyms were not processed. Please try again later.');
        // Filter out the QUOTA_EXHAUSTED entry from results
        data.results = data.results.filter((r: any) => r.acronym !== 'QUOTA_EXHAUSTED');
      }

      // Update progress based on processed count
      if (data.processed_count && data.total_count) {
        const progressPercent = (data.processed_count / data.total_count) * 100;
        setProgress(progressPercent);
      }

      // Process results
      const processedResults = data.results.map((result: any) => ({
        acronym: result.acronym,
        definition: result.definition,
        enrichment: result.enrichment ? {
          description: result.enrichment.description,
          tags: result.enrichment.tags
        } : null
      }));

      setResults(processedResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while processing acronyms');
    } finally {
      setIsProcessing(false);
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

  if (!isAuthenticated) {
    return <Login onLogin={login} />;
  }

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

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </AuthProvider>
  );
};

export default App; 
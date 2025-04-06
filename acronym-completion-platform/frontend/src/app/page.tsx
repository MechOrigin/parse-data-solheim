'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileUpload } from '@/components/FileUpload';
import Settings from '@/components/Settings';
import ProcessingStatus from '@/components/ProcessingStatus';
import Results from '@/components/Results';
import { Result, SettingsState } from '@/types';
import { History } from '@/components/History';
import { EditAcronym } from '@/components/EditAcronym';
import Login from '@/components/Login';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Define the interfaces locally to match the components
interface AcronymResult {
  id: string;
  acronym: string;
  definition: string;
  description: string;
  tags: string[];
  grade: number;
  metadata: Record<string, string>;
  isEnriched?: boolean;
}

interface Acronym {
  acronym: string;
  definition: string;
  description: string;
  tags: string;
  grade: string;
}

export default function Home() {
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [acronymsFile, setAcronymsFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [settings, setSettings] = useState({
    temperature: 0.7,
    maxTokens: 1000
  });
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [selectedAcronym, setSelectedAcronym] = useState<Result | null>(null);
  const [showEditAcronym, setShowEditAcronym] = useState<boolean>(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [history, setHistory] = useState<Result[]>([]);
  const [editingAcronym, setEditingAcronym] = useState<Acronym | null>(null);

  useEffect(() => {
    // Check if we have a stored token
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        setAuthToken(storedToken);
      }
    }

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

  const handleLogin = (token: string) => {
    setAuthToken(token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', token);
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
    }
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
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload template file');
      }
      
      toast.success('Template file uploaded successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while uploading template file';
      setError(errorMessage);
      toast.error(`Template upload failed: ${errorMessage}`);
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
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload acronyms file');
      }
      
      toast.success('Acronyms file uploaded successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while uploading acronyms file';
      setError(errorMessage);
      toast.error(`Acronyms upload failed: ${errorMessage}`);
    }
  };

  const handleSettingsChange = (newSettings: SettingsState) => {
    setSettings(newSettings);
    
    // Update backend configuration
    fetch('http://localhost:8000/update-config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        selectedLLM: newSettings.model,
        geminiApiKey: newSettings.geminiApiKey,
        grokApiKey: newSettings.grokApiKey,
        processingConfig: newSettings.processingConfig
      }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to update configuration');
      }
      return response.json();
    })
    .then(data => {
      console.log('Configuration updated successfully:', data);
    })
    .catch(error => {
      console.error('Error updating configuration:', error);
    });
  };

  const handleDeleteHistory = (id: string) => {
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);
    if (typeof window !== 'undefined') {
      localStorage.setItem('acronymHistory', JSON.stringify(updatedHistory));
    }
  };

  const processAcronyms = async () => {
    if (!templateFile || !acronymsFile) {
      toast.error('Please upload both template and acronyms files');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('template_file', templateFile);
      formData.append('acronyms_file', acronymsFile);

      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process acronyms');
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
      toast.success('Acronyms processed successfully!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      toast.error(`Failed to process acronyms: ${errorMessage}`);
    } finally {
      setIsProcessing(false);
      setProgress(100);
    }
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

  const handleEditAcronym = (acronym: Result) => {
    setEditingAcronym({
      acronym: acronym.acronym,
      definition: acronym.definition,
      description: acronym.description,
      tags: acronym.tags.join(', '),
      grade: acronym.grade.toString()
    });
    setShowEditAcronym(true);
  };

  const handleSaveEdit = (updatedAcronym: Acronym) => {
    if (editingAcronym) {
      const result: Result = {
        id: crypto.randomUUID(),
        acronym: updatedAcronym.acronym,
        definition: updatedAcronym.definition,
        description: updatedAcronym.description,
        tags: updatedAcronym.tags.split(',').map(tag => tag.trim()),
        grade: Number(updatedAcronym.grade),
        metadata: {}
      };
      setResults(results.map(r => r.acronym === editingAcronym.acronym ? result : r));
      setShowEditAcronym(false);
      setEditingAcronym(null);
    }
  };

  const handleRemoveTemplate = () => {
    setTemplateFile(null);
    setError(null);
  };

  const handleRemoveAcronyms = () => {
    setAcronymsFile(null);
    setError(null);
  };

  if (!authToken) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-4 md:p-8">
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Header with logout button */}
        <div className="flex justify-end">
          <button
            onClick={handleLogout}
            className="glass-button"
          >
            Logout
          </button>
        </div>

        {/* File Upload Section */}
        <section className="glass-card">
          <h2 className="enterprise-heading mb-4">Upload Files</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="glass-upload">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => e.target.files?.[0] && handleTemplateUpload(e.target.files[0])}
              />
              <div className="glass-upload-content">
                <svg className="w-8 h-8 mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>{templateFile?.name || 'Upload Template File'}</span>
                {templateFile && (
                  <button
                    onClick={handleRemoveTemplate}
                    className="glass-button mt-2 text-sm"
                  >
                    Remove
                  </button>
                )}
              </div>
            </div>
            <div className="glass-upload">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => e.target.files?.[0] && handleAcronymsUpload(e.target.files[0])}
              />
              <div className="glass-upload-content">
                <svg className="w-8 h-8 mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>{acronymsFile?.name || 'Upload Acronyms File'}</span>
                {acronymsFile && (
                  <button
                    onClick={handleRemoveAcronyms}
                    className="glass-button mt-2 text-sm"
                  >
                    Remove
                  </button>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Settings and Controls */}
        <section className="glass-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="enterprise-heading">Settings</h2>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="glass-button"
            >
              {showSettings ? 'Hide Settings' : 'Show Settings'}
            </button>
          </div>
          {showSettings && (
            <Settings onSettingsChange={handleSettingsChange} />
          )}
        </section>

        {/* Processing Status */}
        <ProcessingStatus
          templateFile={templateFile?.name || null}
          acronymsFile={acronymsFile?.name || null}
          isProcessing={isProcessing}
          progress={progress}
          error={error}
        />

        {/* Process Button */}
        {templateFile && acronymsFile && !isProcessing && (
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="process-button"
            onClick={processAcronyms}
            style={{
              position: 'fixed',
              bottom: '2rem',
              right: '2rem',
              zIndex: 50
            }}
          >
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Process Acronyms
            </span>
          </motion.button>
        )}

        {/* Results Section */}
        {results.length > 0 && (
          <section className="glass-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="enterprise-heading">Results</h2>
              <button
                onClick={downloadResults}
                className="glass-button"
              >
                Download Results
              </button>
            </div>
            <div className="overflow-x-auto">
              <Results
                results={results}
                onUpdateAcronym={handleEditAcronym}
              />
            </div>
          </section>
        )}

        {/* History Section */}
        <section className="glass-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="enterprise-heading">History</h2>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="glass-button"
            >
              {showHistory ? 'Hide History' : 'Show History'}
            </button>
          </div>
          {showHistory && (
            <History
              onSelectHistory={(results: Result[]) => {
                setResults(results);
                setShowHistory(false);
              }}
              onDeleteHistory={handleDeleteHistory}
            />
          )}
        </section>

        {/* Edit Acronym Modal */}
        {showEditAcronym && editingAcronym && (
          <div className="glass-modal">
            <div className="glass-modal-content">
              <div className="glass-modal-header">
                <h3 className="glass-modal-title">Edit Acronym</h3>
                <button
                  onClick={() => setShowEditAcronym(false)}
                  className="glass-modal-close"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <EditAcronym
                acronym={editingAcronym}
                onSave={handleSaveEdit}
                onCancel={() => setShowEditAcronym(false)}
              />
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

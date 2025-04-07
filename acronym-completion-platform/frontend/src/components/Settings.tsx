import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/Settings.css';
import { useTheme } from './ThemeProvider';
import { SettingsState, ProcessingConfig } from '../types';
import { toast } from 'react-hot-toast';

interface SettingsProps {
  onSave: (settings: SettingsState) => void;
}

interface TooltipProps {
  text: string;
  children: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({ text, children }) => {
  return (
    <div className="tooltip-container">
      {children}
      <div className="tooltip">{text}</div>
    </div>
  );
};

const defaultSettings: SettingsState = {
  temperature: 0.7,
  maxTokens: 1000,
  model: 'gemini',
  geminiApiKeys: [''],
  grokApiKey: '',
  processingConfig: {
    batchSize: 250,
    gradeFilter: {
      enabled: false,
      min: 1,
      max: 12,
      singleGrade: undefined,
      gradeRange: undefined
    },
    enrichment: {
      enabled: true,
      addMissingDefinitions: true,
      generateDescriptions: true,
      suggestTags: true,
      useWebSearch: true,
      useInternalKb: true
    },
    startingPoint: {
      enabled: false,
      acronym: undefined
    },
    rateLimiting: {
      enabled: true,
      requestsPerSecond: 60,
      burstSize: 10,
      maxRetries: 3
    },
    outputFormat: {
      includeDefinitions: true,
      includeDescriptions: true,
      includeTags: true,
      includeGrade: true,
      includeMetadata: true
    },
    caching: {
      enabled: true,
      ttlSeconds: 3600
    }
  },
  autoSave: true,
  historyLimit: 50,
  theme: 'system'
};

export const Settings: React.FC<SettingsProps> = ({ onSave }) => {
  const { theme, setTheme } = useTheme();
  const [settings, setSettings] = useState<SettingsState>(defaultSettings);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'ai' | 'processing' | 'appearance' | 'advanced' | 'rateLimiting' | 'output' | 'caching'>('ai');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('acronymSettings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(prevSettings => ({
          ...prevSettings,
          ...parsedSettings
        }));
        
        // Apply theme from settings
        if (parsedSettings.theme) {
          setTheme(parsedSettings.theme);
        }
      } catch (err) {
        console.error('Error loading settings:', err);
      }
    }
  }, [setTheme]);

  // Save settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem('acronymSettings', JSON.stringify(settings));
    onSave(settings);
  }, [settings, onSave]);

  const validateSetting = (name: string, value: any): string | undefined => {
    switch (name) {
      case 'temperature':
        if (value < 0 || value > 1) {
          return 'Temperature must be between 0 and 1';
        }
        break;
      case 'maxTokens':
        if (value < 100 || value > 2000) {
          return 'Max tokens must be between 100 and 2000';
        }
        break;
      case 'batchSize':
        if (value < 1 || value > 250) {
          return 'Batch size must be between 1 and 250';
        }
        break;
      case 'historyLimit':
        if (value < 10 || value > 100) {
          return 'History limit must be between 10 and 100';
        }
        break;
      case 'requestsPerSecond':
        if (value < 0.1 || value > 10) {
          return 'Requests per second must be between 0.1 and 10';
        }
        break;
      case 'burstSize':
        if (value < 1 || value > 10) {
          return 'Burst size must be between 1 and 10';
        }
        break;
      case 'maxRetries':
        if (value < 0 || value > 10) {
          return 'Max retries must be between 0 and 10';
        }
        break;
      case 'ttlSeconds':
        if (value < 60 || value > 604800) {
          return 'TTL must be between 60 seconds and 7 days';
        }
        break;
      case 'gradeFilter.min':
        if (value < 1 || value > 12) {
          return 'Min grade must be between 1 and 12';
        }
        const maxGrade = settings.processingConfig.gradeFilter.max;
        if (maxGrade !== undefined && value > maxGrade) {
          return 'Min grade cannot be greater than max grade';
        }
        break;
      case 'gradeFilter.max':
        if (value < 1 || value > 12) {
          return 'Max grade must be between 1 and 12';
        }
        const minGrade = settings.processingConfig.gradeFilter.min;
        if (minGrade !== undefined && value < minGrade) {
          return 'Max grade cannot be less than min grade';
        }
        break;
    }
    return undefined;
  };

  const handleSettingChange = (name: keyof SettingsState, value: any) => {
    const error = validateSetting(name, value);
    setErrors(prev => {
      const newErrors = { ...prev };
      if (error) {
        newErrors[name] = error;
      } else {
        delete newErrors[name];
      }
      return newErrors;
    });
    
    if (!error) {
      const newSettings = { ...settings, [name]: value };
      setSettings(newSettings);
      
      // If theme is changed, update the theme context
      if (name === 'theme') {
        setTheme(value);
      }
    }
  };

  const handleProcessingConfigChange = (key: keyof ProcessingConfig, value: any) => {
    const newProcessingConfig = { ...settings.processingConfig, [key]: value };
    handleSettingChange('processingConfig', newProcessingConfig);
  };

  const handleProcessingConfigFieldChange = (section: keyof ProcessingConfig, field: string, value: any) => {
    const newProcessingConfig = { ...settings.processingConfig };
    const currentSection = newProcessingConfig[section] as Record<string, any>;
    if (currentSection) {
      currentSection[field] = value;
      handleSettingChange('processingConfig', newProcessingConfig);
    }
  };

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleTabChange = (tab: 'ai' | 'processing' | 'appearance' | 'advanced' | 'rateLimiting' | 'output' | 'caching') => {
    setActiveTab(tab);
  };

  const handleGradeFilterChange = (key: 'enabled' | 'singleGrade' | 'gradeRange', value: any) => {
    const newGradeFilter = { ...settings.processingConfig.gradeFilter, [key]: value };
    handleProcessingConfigChange('gradeFilter', newGradeFilter);
  };

  const handleEnrichmentChange = (key: string, value: any) => {
    const newEnrichment = { ...settings.processingConfig.enrichment, [key]: value };
    handleProcessingConfigChange('enrichment', newEnrichment);
  };

  const handleRateLimitingChange = (key: string, value: any) => {
    const newRateLimiting = { ...settings.processingConfig.rateLimiting, [key]: value };
    handleProcessingConfigChange('rateLimiting', newRateLimiting);
  };

  const handleOutputFormatChange = (key: string, value: any) => {
    const newOutputFormat = { ...settings.processingConfig.outputFormat, [key]: value };
    handleProcessingConfigChange('outputFormat', newOutputFormat);
  };

  const handleCachingChange = (key: string, value: any) => {
    const newCaching = { ...settings.processingConfig.caching, [key]: value };
    handleProcessingConfigChange('caching', newCaching);
  };

  const handleResetToDefaults = () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      setSettings(defaultSettings);
      setTheme(defaultSettings.theme);
    }
  };

  const handleExportSettings = () => {
    const settingsJson = JSON.stringify(settings, null, 2);
    const blob = new Blob([settingsJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'acronym-settings.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target?.result as string);
          setSettings(prevSettings => ({
            ...prevSettings,
            ...importedSettings
          }));
          if (importedSettings.theme) {
            setTheme(importedSettings.theme);
          }
        } catch (err) {
          console.error('Error importing settings:', err);
          alert('Error importing settings. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleKeyPress = (event: KeyboardEvent) => {
    if (event.key === 'Escape' && isExpanded) {
      setIsExpanded(false);
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isExpanded]);

  const filteredTabs = ['ai', 'processing', 'appearance', 'advanced', 'rateLimiting', 'output', 'caching'].filter(tab => 
    tab.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSave = async () => {
    try {
      const response = await fetch('/api/update-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      toast.success('Settings saved successfully');
      onSave(settings);
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`settings-container ${theme}`}
    >
      <div className="settings-header" onClick={handleToggleExpand}>
        <h2>Settings</h2>
        <div className="settings-actions">
          <input
            type="text"
            placeholder="Search settings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="settings-search"
            onClick={(e) => e.stopPropagation()}
          />
          <button onClick={(e) => { e.stopPropagation(); handleResetToDefaults(); }} className="settings-action-button">
            Reset to Defaults
          </button>
          <button onClick={(e) => { e.stopPropagation(); handleExportSettings(); }} className="settings-action-button">
            Export
          </button>
          <label className="settings-action-button">
            Import
            <input
              type="file"
              accept=".json"
              onChange={handleImportSettings}
              style={{ display: 'none' }}
            />
          </label>
          <motion.div 
            className="expand-icon"
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </motion.div>
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="settings-content"
          >
            <div className="settings-tabs">
              {filteredTabs.map(tab => (
                <button 
                  key={tab}
                  className={`tab-button ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => handleTabChange(tab as any)}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="settings-panel">
              <AnimatePresence mode="wait">
                {activeTab === 'ai' && (
                  <motion.div
                    key="ai"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>AI Model Settings</h3>
                    <div className="setting-group">
                      <Tooltip text="Choose the AI model for processing">
                        <label>Model</label>
                      </Tooltip>
                      <select 
                        value={settings.model} 
                        onChange={(e) => handleSettingChange('model', e.target.value)}
                      >
                        <option value="gemini">Gemini</option>
                        <option value="grok">Grok</option>
                      </select>
                    </div>
                    <div className="setting-group">
                      <Tooltip text="Controls randomness in the output. Lower values are more deterministic">
                        <label>Temperature</label>
                      </Tooltip>
                      <input 
                        type="range" 
                        min="0" 
                        max="1" 
                        step="0.1" 
                        value={settings.temperature} 
                        onChange={(e) => handleSettingChange('temperature', parseFloat(e.target.value))}
                      />
                      <span>{settings.temperature}</span>
                      {errors.temperature && <span className="error">{errors.temperature}</span>}
                    </div>
                    <div className="setting-group">
                      <Tooltip text="Maximum number of tokens in the response">
                        <label>Max Tokens</label>
                      </Tooltip>
                      <input 
                        type="number" 
                        min="100" 
                        max="2000" 
                        value={settings.maxTokens} 
                        onChange={(e) => handleSettingChange('maxTokens', parseInt(e.target.value))}
                      />
                      {errors.maxTokens && <span className="error">{errors.maxTokens}</span>}
                    </div>
                  </motion.div>
                )}

                {activeTab === 'processing' && (
                  <motion.div
                    key="processing"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Processing Settings</h3>
                    <div className="setting-group">
                      <label>Batch Size</label>
                      <input
                        type="number"
                        min="1"
                        max="250"
                        value={settings.processingConfig.batchSize}
                        onChange={(e) => {
                          const value = e.target.value === '' ? 1 : parseInt(e.target.value);
                          if (!isNaN(value) && value >= 1 && value <= 250) {
                            handleProcessingConfigChange('batchSize', value);
                          }
                        }}
                        onBlur={(e) => {
                          if (e.target.value === '' || parseInt(e.target.value) < 1) {
                            handleProcessingConfigChange('batchSize', 1);
                          }
                        }}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                      <p className="mt-1 text-sm text-gray-500">Number of acronyms to process at once (1-250)</p>
                    </div>

                    <div className="setting-group">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.enrichment.enabled}
                          onChange={(e) => handleEnrichmentChange('enabled', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm font-medium text-gray-700">Enable AI Processing</span>
                      </label>
                      <div className="ml-6 mt-2 space-y-2">
                        <div className="checkbox-group">
                          <input
                            type="checkbox"
                            checked={settings.processingConfig.enrichment.addMissingDefinitions}
                            onChange={(e) => handleEnrichmentChange('addMissingDefinitions', e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span>Generate Missing Definitions</span>
                        </div>
                        <div className="checkbox-group">
                          <input
                            type="checkbox"
                            checked={settings.processingConfig.enrichment.generateDescriptions}
                            onChange={(e) => handleEnrichmentChange('generateDescriptions', e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span>Generate Descriptions</span>
                        </div>
                        <div className="checkbox-group">
                          <input
                            type="checkbox"
                            checked={settings.processingConfig.enrichment.suggestTags}
                            onChange={(e) => handleEnrichmentChange('suggestTags', e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span>Suggest Tags</span>
                        </div>
                        <div className="checkbox-group">
                          <input
                            type="checkbox"
                            checked={settings.processingConfig.enrichment.useWebSearch}
                            onChange={(e) => handleEnrichmentChange('useWebSearch', e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span>Use Web Search</span>
                        </div>
                        <div className="checkbox-group">
                          <input
                            type="checkbox"
                            checked={settings.processingConfig.enrichment.useInternalKb}
                            onChange={(e) => handleEnrichmentChange('useInternalKb', e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span>Use Internal Knowledge Base</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'rateLimiting' && (
                  <motion.div
                    key="rateLimiting"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Rate Limiting Settings</h3>
                    <div className="setting-group">
                      <label>Enable Rate Limiting</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.processingConfig.rateLimiting.enabled} 
                          onChange={(e) => handleRateLimitingChange('enabled', e.target.checked)}
                        />
                        <span>Enable API Rate Limiting</span>
                      </div>
                    </div>
                    {settings.processingConfig.rateLimiting.enabled && (
                      <div className="sub-settings">
                        <div className="setting-group">
                          <label>Requests Per Second</label>
                          <input 
                            type="number" 
                            min="0.1" 
                            max="10" 
                            step="0.1" 
                            value={settings.processingConfig.rateLimiting.requestsPerSecond} 
                            onChange={(e) => handleRateLimitingChange('requestsPerSecond', parseFloat(e.target.value))}
                          />
                          {errors.requestsPerSecond && <span className="error">{errors.requestsPerSecond}</span>}
                        </div>
                        <div className="setting-group">
                          <label>Burst Size</label>
                          <input 
                            type="number" 
                            min="1" 
                            max="10" 
                            value={settings.processingConfig.rateLimiting.burstSize} 
                            onChange={(e) => handleRateLimitingChange('burstSize', parseInt(e.target.value))}
                          />
                          {errors.burstSize && <span className="error">{errors.burstSize}</span>}
                        </div>
                        <div className="setting-group">
                          <label>Max Retries</label>
                          <input 
                            type="number" 
                            min="0" 
                            max="10" 
                            value={settings.processingConfig.rateLimiting.maxRetries} 
                            onChange={(e) => handleRateLimitingChange('maxRetries', parseInt(e.target.value))}
                          />
                          {errors.maxRetries && <span className="error">{errors.maxRetries}</span>}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {activeTab === 'output' && (
                  <motion.div
                    key="output"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Output Display Settings</h3>
                    <p className="text-sm text-gray-500 mb-4">Configure which fields to display in the results table</p>
                    <div className="setting-group">
                      <div className="checkbox-group">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.outputFormat.includeDefinitions}
                          onChange={(e) => handleOutputFormatChange('includeDefinitions', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Show Definitions Column</span>
                      </div>
                      <div className="checkbox-group">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.outputFormat.includeDescriptions}
                          onChange={(e) => handleOutputFormatChange('includeDescriptions', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Show Descriptions Column</span>
                      </div>
                      <div className="checkbox-group">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.outputFormat.includeTags}
                          onChange={(e) => handleOutputFormatChange('includeTags', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Show Tags Column</span>
                      </div>
                      <div className="checkbox-group">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.outputFormat.includeGrade}
                          onChange={(e) => handleOutputFormatChange('includeGrade', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Show Grade Column</span>
                      </div>
                      <div className="checkbox-group">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.outputFormat.includeMetadata}
                          onChange={(e) => handleOutputFormatChange('includeMetadata', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Show Metadata Column</span>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'caching' && (
                  <motion.div
                    key="caching"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Caching Settings</h3>
                    <div className="setting-group">
                      <label>Enable Caching</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.processingConfig.caching.enabled} 
                          onChange={(e) => handleCachingChange('enabled', e.target.checked)}
                        />
                        <span>Enable Response Caching</span>
                      </div>
                    </div>
                    {settings.processingConfig.caching.enabled && (
                      <div className="sub-settings">
                        <div className="setting-group">
                          <label>Cache TTL (seconds)</label>
                          <input 
                            type="number" 
                            min="60" 
                            max="604800" 
                            value={settings.processingConfig.caching.ttlSeconds} 
                            onChange={(e) => handleCachingChange('ttlSeconds', parseInt(e.target.value))}
                          />
                          {errors.ttlSeconds && <span className="error">{errors.ttlSeconds}</span>}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {activeTab === 'appearance' && (
                  <motion.div
                    key="appearance"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Appearance Settings</h3>
                    <div className="setting-group">
                      <label>Theme</label>
                      <select 
                        value={settings.theme} 
                        onChange={(e) => handleSettingChange('theme', e.target.value)}
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="system">System</option>
                      </select>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'advanced' && (
                  <motion.div
                    key="advanced"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Advanced Settings</h3>
                    <div className="setting-group">
                      <label>Auto Save</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.autoSave} 
                          onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                        />
                        <span>Automatically Save Results</span>
                      </div>
                    </div>
                    <div className="setting-group">
                      <label>History Limit</label>
                      <input 
                        type="number" 
                        min="10" 
                        max="100" 
                        value={settings.historyLimit} 
                        onChange={(e) => handleSettingChange('historyLimit', parseInt(e.target.value))}
                      />
                      {errors.historyLimit && <span className="error">{errors.historyLimit}</span>}
                    </div>
                  </motion.div>
                )}

                {activeTab === 'processing' && (
                  <motion.div
                    key="gradeFilter"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="settings-section"
                  >
                    <h3>Grade Filter Settings</h3>
                    <div className="setting-group">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={settings.processingConfig.gradeFilter.enabled}
                          onChange={(e) => handleGradeFilterChange('enabled', e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm font-medium text-gray-700">Enable Grade Filtering</span>
                      </label>
                      
                      {settings.processingConfig.gradeFilter.enabled && (
                        <div className="mt-2 ml-6 space-y-2">
                          <div>
                            <label className="block text-sm text-gray-600">Filter Type</label>
                            <select
                              value={settings.processingConfig.gradeFilter.singleGrade !== undefined ? 'single' : 'range'}
                              onChange={(e) => {
                                const isSingle = e.target.value === 'single';
                                handleGradeFilterChange('singleGrade', isSingle ? '' : undefined);
                                handleGradeFilterChange('gradeRange', isSingle ? undefined : { start: '', end: '' });
                              }}
                              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            >
                              <option value="single">Single Grade</option>
                              <option value="range">Grade Range</option>
                            </select>
                          </div>

                          {settings.processingConfig.gradeFilter.singleGrade !== undefined ? (
                            <div>
                              <label className="block text-sm text-gray-600">Grade</label>
                              <input
                                type="text"
                                value={settings.processingConfig.gradeFilter.singleGrade || ''}
                                onChange={(e) => handleGradeFilterChange('singleGrade', e.target.value)}
                                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                                  errors.singleGrade ? 'border-red-500' : ''
                                }`}
                              />
                              {errors.singleGrade && (
                                <p className="mt-1 text-sm text-red-600">{errors.singleGrade}</p>
                              )}
                            </div>
                          ) : (
                            <div className="space-y-2">
                              <div>
                                <label className="block text-sm text-gray-600">Start Grade</label>
                                <input
                                  type="text"
                                  value={settings.processingConfig.gradeFilter.gradeRange?.start || ''}
                                  onChange={(e) => handleGradeFilterChange('gradeRange', {
                                    ...settings.processingConfig.gradeFilter.gradeRange,
                                    start: e.target.value
                                  })}
                                  className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                                    errors.gradeRange ? 'border-red-500' : ''
                                  }`}
                                />
                              </div>
                              <div>
                                <label className="block text-sm text-gray-600">End Grade</label>
                                <input
                                  type="text"
                                  value={settings.processingConfig.gradeFilter.gradeRange?.end || ''}
                                  onChange={(e) => handleGradeFilterChange('gradeRange', {
                                    ...settings.processingConfig.gradeFilter.gradeRange,
                                    end: e.target.value
                                  })}
                                  className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                                    errors.gradeRange ? 'border-red-500' : ''
                                  }`}
                                />
                              </div>
                              {errors.gradeRange && (
                                <p className="mt-1 text-sm text-red-600">{errors.gradeRange}</p>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button onClick={handleSave} className="save-button">
        Save Settings
      </button>
    </motion.div>
  );
};

export default Settings; 
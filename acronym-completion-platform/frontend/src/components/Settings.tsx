import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/Settings.css';
import { useTheme } from './ThemeProvider';

interface SettingsProps {
  onSettingsChange: (settings: SettingsState) => void;
}

interface SettingsState {
  temperature: number;
  maxTokens: number;
  model: 'grok' | 'gemini';
  batchSize: number;
  autoSave: boolean;
  historyLimit: number;
  theme: 'light' | 'dark' | 'system';
  gradeFilter: {
    enabled: boolean;
    min: number;
    max: number;
  };
  selectiveEnrichment: boolean;
  enrichment: {
    enabled: boolean;
    addMissingDefinitions: boolean;
    generateDescriptions: boolean;
    suggestTags: boolean;
    useWebSearch: boolean;
    useInternalKb: boolean;
  };
  rateLimiting: {
    enabled: boolean;
    requestsPerSecond: number;
    burstSize: number;
    maxRetries: number;
  };
  outputFormat: {
    includeDefinitions: boolean;
    includeDescriptions: boolean;
    includeTags: boolean;
    includeGrade: boolean;
    includeMetadata: boolean;
  };
  caching: {
    enabled: boolean;
    ttlSeconds: number;
  };
}

const defaultSettings: SettingsState = {
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
};

const Settings: React.FC<SettingsProps> = ({ onSettingsChange }) => {
  const [settings, setSettings] = useState<SettingsState>(defaultSettings);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'ai' | 'processing' | 'appearance' | 'advanced' | 'rateLimiting' | 'output' | 'caching'>('ai');
  const { theme, setTheme } = useTheme();

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
    onSettingsChange(settings);
  }, [settings, onSettingsChange]);

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
        if (value < 1 || value > 50) {
          return 'Batch size must be between 1 and 50';
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

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleTabChange = (tab: 'ai' | 'processing' | 'appearance' | 'advanced' | 'rateLimiting' | 'output' | 'caching') => {
    setActiveTab(tab);
  };

  const handleGradeFilterChange = (key: 'enabled' | 'min' | 'max', value: any) => {
    const newGradeFilter = { ...settings.gradeFilter, [key]: value };
    handleSettingChange('gradeFilter', newGradeFilter);
  };

  const handleEnrichmentChange = (key: string, value: any) => {
    const newEnrichment = { ...settings.enrichment, [key]: value };
    handleSettingChange('enrichment', newEnrichment);
  };

  const handleRateLimitingChange = (key: string, value: any) => {
    const newRateLimiting = { ...settings.rateLimiting, [key]: value };
    handleSettingChange('rateLimiting', newRateLimiting);
  };

  const handleOutputFormatChange = (key: string, value: any) => {
    const newOutputFormat = { ...settings.outputFormat, [key]: value };
    handleSettingChange('outputFormat', newOutputFormat);
  };

  const handleCachingChange = (key: string, value: any) => {
    const newCaching = { ...settings.caching, [key]: value };
    handleSettingChange('caching', newCaching);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="settings-container"
    >
      <div className="settings-header" onClick={handleToggleExpand}>
        <h2>Settings</h2>
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
              <button 
                className={`tab-button ${activeTab === 'ai' ? 'active' : ''}`}
                onClick={() => handleTabChange('ai')}
              >
                AI Model
              </button>
              <button 
                className={`tab-button ${activeTab === 'processing' ? 'active' : ''}`}
                onClick={() => handleTabChange('processing')}
              >
                Processing
              </button>
              <button 
                className={`tab-button ${activeTab === 'rateLimiting' ? 'active' : ''}`}
                onClick={() => handleTabChange('rateLimiting')}
              >
                Rate Limiting
              </button>
              <button 
                className={`tab-button ${activeTab === 'output' ? 'active' : ''}`}
                onClick={() => handleTabChange('output')}
              >
                Output
              </button>
              <button 
                className={`tab-button ${activeTab === 'caching' ? 'active' : ''}`}
                onClick={() => handleTabChange('caching')}
              >
                Caching
              </button>
              <button 
                className={`tab-button ${activeTab === 'appearance' ? 'active' : ''}`}
                onClick={() => handleTabChange('appearance')}
              >
                Appearance
              </button>
              <button 
                className={`tab-button ${activeTab === 'advanced' ? 'active' : ''}`}
                onClick={() => handleTabChange('advanced')}
              >
                Advanced
              </button>
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
                      <label>Model</label>
                      <select 
                        value={settings.model} 
                        onChange={(e) => handleSettingChange('model', e.target.value)}
                      >
                        <option value="gemini">Gemini</option>
                        <option value="grok">Grok</option>
                      </select>
                    </div>
                    <div className="setting-group">
                      <label>Temperature</label>
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
                      <label>Max Tokens</label>
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
                        max="50" 
                        value={settings.batchSize} 
                        onChange={(e) => handleSettingChange('batchSize', parseInt(e.target.value))}
                      />
                      {errors.batchSize && <span className="error">{errors.batchSize}</span>}
                    </div>
                    <div className="setting-group">
                      <label>Grade Filter</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.gradeFilter.enabled} 
                          onChange={(e) => handleGradeFilterChange('enabled', e.target.checked)}
                        />
                        <span>Enable Grade Filtering</span>
                      </div>
                      {settings.gradeFilter.enabled && (
                        <div className="sub-settings">
                          <div className="setting-group">
                            <label>Min Grade</label>
                            <input 
                              type="number" 
                              min="1" 
                              max="12" 
                              value={settings.gradeFilter.min} 
                              onChange={(e) => handleGradeFilterChange('min', parseInt(e.target.value))}
                            />
                          </div>
                          <div className="setting-group">
                            <label>Max Grade</label>
                            <input 
                              type="number" 
                              min="1" 
                              max="12" 
                              value={settings.gradeFilter.max} 
                              onChange={(e) => handleGradeFilterChange('max', parseInt(e.target.value))}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="setting-group">
                      <label>Enrichment</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.enrichment.enabled} 
                          onChange={(e) => handleEnrichmentChange('enabled', e.target.checked)}
                        />
                        <span>Enable Enrichment</span>
                      </div>
                      {settings.enrichment.enabled && (
                        <div className="sub-settings">
                          <div className="checkbox-group">
                            <input 
                              type="checkbox" 
                              checked={settings.enrichment.addMissingDefinitions} 
                              onChange={(e) => handleEnrichmentChange('addMissingDefinitions', e.target.checked)}
                            />
                            <span>Add Missing Definitions</span>
                          </div>
                          <div className="checkbox-group">
                            <input 
                              type="checkbox" 
                              checked={settings.enrichment.generateDescriptions} 
                              onChange={(e) => handleEnrichmentChange('generateDescriptions', e.target.checked)}
                            />
                            <span>Generate Descriptions</span>
                          </div>
                          <div className="checkbox-group">
                            <input 
                              type="checkbox" 
                              checked={settings.enrichment.suggestTags} 
                              onChange={(e) => handleEnrichmentChange('suggestTags', e.target.checked)}
                            />
                            <span>Suggest Tags</span>
                          </div>
                          <div className="checkbox-group">
                            <input 
                              type="checkbox" 
                              checked={settings.enrichment.useWebSearch} 
                              onChange={(e) => handleEnrichmentChange('useWebSearch', e.target.checked)}
                            />
                            <span>Use Web Search</span>
                          </div>
                          <div className="checkbox-group">
                            <input 
                              type="checkbox" 
                              checked={settings.enrichment.useInternalKb} 
                              onChange={(e) => handleEnrichmentChange('useInternalKb', e.target.checked)}
                            />
                            <span>Use Internal Knowledge Base</span>
                          </div>
                        </div>
                      )}
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
                          checked={settings.rateLimiting.enabled} 
                          onChange={(e) => handleRateLimitingChange('enabled', e.target.checked)}
                        />
                        <span>Enable API Rate Limiting</span>
                      </div>
                    </div>
                    {settings.rateLimiting.enabled && (
                      <div className="sub-settings">
                        <div className="setting-group">
                          <label>Requests Per Second</label>
                          <input 
                            type="number" 
                            min="0.1" 
                            max="10" 
                            step="0.1" 
                            value={settings.rateLimiting.requestsPerSecond} 
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
                            value={settings.rateLimiting.burstSize} 
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
                            value={settings.rateLimiting.maxRetries} 
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
                    <h3>Output Format Settings</h3>
                    <div className="setting-group">
                      <label>Include Definitions</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.outputFormat.includeDefinitions} 
                          onChange={(e) => handleOutputFormatChange('includeDefinitions', e.target.checked)}
                        />
                        <span>Include Definitions in Output</span>
                      </div>
                    </div>
                    <div className="setting-group">
                      <label>Include Descriptions</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.outputFormat.includeDescriptions} 
                          onChange={(e) => handleOutputFormatChange('includeDescriptions', e.target.checked)}
                        />
                        <span>Include Descriptions in Output</span>
                      </div>
                    </div>
                    <div className="setting-group">
                      <label>Include Tags</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.outputFormat.includeTags} 
                          onChange={(e) => handleOutputFormatChange('includeTags', e.target.checked)}
                        />
                        <span>Include Tags in Output</span>
                      </div>
                    </div>
                    <div className="setting-group">
                      <label>Include Grade</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.outputFormat.includeGrade} 
                          onChange={(e) => handleOutputFormatChange('includeGrade', e.target.checked)}
                        />
                        <span>Include Grade in Output</span>
                      </div>
                    </div>
                    <div className="setting-group">
                      <label>Include Metadata</label>
                      <div className="checkbox-group">
                        <input 
                          type="checkbox" 
                          checked={settings.outputFormat.includeMetadata} 
                          onChange={(e) => handleOutputFormatChange('includeMetadata', e.target.checked)}
                        />
                        <span>Include Metadata in Output</span>
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
                          checked={settings.caching.enabled} 
                          onChange={(e) => handleCachingChange('enabled', e.target.checked)}
                        />
                        <span>Enable Response Caching</span>
                      </div>
                    </div>
                    {settings.caching.enabled && (
                      <div className="sub-settings">
                        <div className="setting-group">
                          <label>Cache TTL (seconds)</label>
                          <input 
                            type="number" 
                            min="60" 
                            max="604800" 
                            value={settings.caching.ttlSeconds} 
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
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default Settings; 
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ProcessingConfig } from '../types';

interface ConfigurationProps {
  onSave: (config: Config) => void;
}

interface Config {
  geminiApiKey: string;
  grokApiKey: string;
  selectedLLM: 'gemini' | 'grok';
  processingConfig: ProcessingConfig;
  gradePrompt: string;
}

const Configuration: React.FC<ConfigurationProps> = ({ onSave }) => {
  const [config, setConfig] = useState<Config>({
    geminiApiKey: '',
    grokApiKey: '',
    selectedLLM: 'gemini',
    processingConfig: {
      batchSize: 25,
      gradeFilter: {
        enabled: false,
        singleGrade: undefined,
        gradeRange: undefined
      },
      enrichment: {
        enabled: true
      },
      startingPoint: {
        enabled: false,
        acronym: ''
      }
    },
    gradePrompt: 'Please provide a clear and concise definition for this acronym, suitable for grade {grade} students.'
  });

  const [isEditing, setIsEditing] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    // Load saved configuration from localStorage
    const savedConfig = localStorage.getItem('llmConfig');
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }
  }, []);

  const validateConfig = (config: Config): Record<string, string> => {
    const errors: Record<string, string> = {};
    
    // Validate batch size
    if (config.processingConfig.batchSize < 1 || config.processingConfig.batchSize > 250) {
      errors.batchSize = 'Batch size must be between 1 and 250';
    }
    
    // Validate grade filter
    if (config.processingConfig.gradeFilter.enabled) {
      if (config.processingConfig.gradeFilter.singleGrade !== undefined) {
        if (!config.processingConfig.gradeFilter.singleGrade) {
          errors.singleGrade = 'Single grade is required when enabled';
        }
      } else if (config.processingConfig.gradeFilter.gradeRange) {
        if (!config.processingConfig.gradeFilter.gradeRange.start || !config.processingConfig.gradeFilter.gradeRange.end) {
          errors.gradeRange = 'Both start and end grades are required for grade range';
        }
      }
    }
    
    // Validate starting point
    if (config.processingConfig.startingPoint.enabled && !config.processingConfig.startingPoint.acronym) {
      errors.startingPoint = 'Starting acronym is required when enabled';
    }
    
    return errors;
  };

  const handleSave = () => {
    const validationErrors = validateConfig(config);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    
    localStorage.setItem('llmConfig', JSON.stringify(config));
    onSave(config);
    setIsEditing(false);
    setErrors({});
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-lg p-6 mb-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Configuration</h2>
        <div className="space-x-2">
          {isEditing && (
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Save
            </button>
          )}
          <button
            onClick={() => setIsEditing(!isEditing)}
            className={`px-4 py-2 rounded-md ${
              isEditing 
                ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            } focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* API Configuration */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-medium text-gray-800 mb-4">API Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Selected LLM</label>
              <select
                value={config.selectedLLM}
                onChange={(e) => setConfig({ ...config, selectedLLM: e.target.value as 'gemini' | 'grok' })}
                disabled={!isEditing}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="gemini">Gemini</option>
                <option value="grok">Grok</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Gemini API Key</label>
              <input
                type="password"
                value={config.geminiApiKey}
                onChange={(e) => setConfig({ ...config, geminiApiKey: e.target.value })}
                disabled={!isEditing}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Grok API Key</label>
              <input
                type="password"
                value={config.grokApiKey}
                onChange={(e) => setConfig({ ...config, grokApiKey: e.target.value })}
                disabled={!isEditing}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Processing Configuration */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Processing Configuration</h3>
          
          <div className="space-y-4">
            {/* Batch Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Batch Size</label>
              <input
                type="number"
                min="1"
                max="250"
                value={config.processingConfig.batchSize}
                onChange={(e) => setConfig({
                  ...config,
                  processingConfig: {
                    ...config.processingConfig,
                    batchSize: parseInt(e.target.value)
                  }
                })}
                disabled={!isEditing}
                className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                  errors.batchSize ? 'border-red-500' : ''
                }`}
              />
              <p className="mt-1 text-sm text-gray-500">Number of acronyms to process at once (1-250)</p>
              {errors.batchSize && (
                <p className="mt-1 text-sm text-red-600">{errors.batchSize}</p>
              )}
            </div>

            {/* Grade Filter */}
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={config.processingConfig.gradeFilter.enabled}
                  onChange={(e) => setConfig({
                    ...config,
                    processingConfig: {
                      ...config.processingConfig,
                      gradeFilter: {
                        ...config.processingConfig.gradeFilter,
                        enabled: e.target.checked
                      }
                    }
                  })}
                  disabled={!isEditing}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable Grade Filtering</span>
              </label>
              
              {config.processingConfig.gradeFilter.enabled && (
                <div className="mt-2 ml-6 space-y-2">
                  <div>
                    <label className="block text-sm text-gray-600">Filter Type</label>
                    <select
                      value={config.processingConfig.gradeFilter.singleGrade !== undefined ? 'single' : 'range'}
                      onChange={(e) => {
                        const isSingle = e.target.value === 'single';
                        setConfig({
                          ...config,
                          processingConfig: {
                            ...config.processingConfig,
                            gradeFilter: {
                              ...config.processingConfig.gradeFilter,
                              singleGrade: isSingle ? '' : undefined,
                              gradeRange: isSingle ? undefined : { start: '', end: '' }
                            }
                          }
                        });
                      }}
                      disabled={!isEditing}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="single">Single Grade</option>
                      <option value="range">Grade Range</option>
                    </select>
                  </div>

                  {config.processingConfig.gradeFilter.singleGrade !== undefined ? (
                    <div>
                      <label className="block text-sm text-gray-600">Grade</label>
                      <input
                        type="text"
                        value={config.processingConfig.gradeFilter.singleGrade}
                        onChange={(e) => setConfig({
                          ...config,
                          processingConfig: {
                            ...config.processingConfig,
                            gradeFilter: {
                              ...config.processingConfig.gradeFilter,
                              singleGrade: e.target.value
                            }
                          }
                        })}
                        disabled={!isEditing}
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
                          value={config.processingConfig.gradeFilter.gradeRange?.start || ''}
                          onChange={(e) => setConfig({
                            ...config,
                            processingConfig: {
                              ...config.processingConfig,
                              gradeFilter: {
                                ...config.processingConfig.gradeFilter,
                                gradeRange: {
                                  ...config.processingConfig.gradeFilter.gradeRange!,
                                  start: e.target.value
                                }
                              }
                            }
                          })}
                          disabled={!isEditing}
                          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                            errors.gradeRange ? 'border-red-500' : ''
                          }`}
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-600">End Grade</label>
                        <input
                          type="text"
                          value={config.processingConfig.gradeFilter.gradeRange?.end || ''}
                          onChange={(e) => setConfig({
                            ...config,
                            processingConfig: {
                              ...config.processingConfig,
                              gradeFilter: {
                                ...config.processingConfig.gradeFilter,
                                gradeRange: {
                                  ...config.processingConfig.gradeFilter.gradeRange!,
                                  end: e.target.value
                                }
                              }
                            }
                          })}
                          disabled={!isEditing}
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

            {/* Acronym Enrichment */}
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={config.processingConfig.enrichment.enabled}
                  onChange={(e) => setConfig({
                    ...config,
                    processingConfig: {
                      ...config.processingConfig,
                      enrichment: {
                        ...config.processingConfig.enrichment,
                        enabled: e.target.checked
                      }
                    }
                  })}
                  disabled={!isEditing}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable Acronym Enrichment</span>
              </label>
              <p className="mt-1 text-sm text-gray-500">Add AI-powered definitions, descriptions, and tags to acronyms</p>
            </div>

            {/* Starting Point */}
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={config.processingConfig.startingPoint.enabled}
                  onChange={(e) => setConfig({
                    ...config,
                    processingConfig: {
                      ...config.processingConfig,
                      startingPoint: {
                        ...config.processingConfig.startingPoint,
                        enabled: e.target.checked
                      }
                    }
                  })}
                  disabled={!isEditing}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable Starting Point</span>
              </label>
              
              {config.processingConfig.startingPoint.enabled && (
                <div className="mt-2 ml-6">
                  <label className="block text-sm text-gray-600">Starting Acronym</label>
                  <input
                    type="text"
                    value={config.processingConfig.startingPoint.acronym}
                    onChange={(e) => setConfig({
                      ...config,
                      processingConfig: {
                        ...config.processingConfig,
                        startingPoint: {
                          ...config.processingConfig.startingPoint,
                          acronym: e.target.value
                        }
                      }
                    })}
                    disabled={!isEditing}
                    className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
                      errors.startingPoint ? 'border-red-500' : ''
                    }`}
                    placeholder="Enter acronym to start from"
                  />
                  {errors.startingPoint && (
                    <p className="mt-1 text-sm text-red-600">{errors.startingPoint}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Grade Prompt */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Grade Prompt</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700">Custom Grade Prompt</label>
            <textarea
              value={config.gradePrompt}
              onChange={(e) => setConfig({ ...config, gradePrompt: e.target.value })}
              disabled={!isEditing}
              rows={3}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Enter custom prompt for grade-specific definitions"
            />
            <p className="mt-1 text-sm text-gray-500">
              Use {'{grade}'} as a placeholder for the grade level
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Configuration; 
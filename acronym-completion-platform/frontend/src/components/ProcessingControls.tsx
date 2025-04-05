import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface ProcessingControlsProps {
  onProcess: (settings: ProcessingSettings) => void;
  isProcessing: boolean;
}

interface ProcessingSettings {
  startFromAcronym: string;
  grade: number;
  batchSize: number;
}

const ProcessingControls: React.FC<ProcessingControlsProps> = ({ onProcess, isProcessing }) => {
  const [settings, setSettings] = useState<ProcessingSettings>({
    startFromAcronym: '',
    grade: 2,
    batchSize: 10
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onProcess(settings);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-lg p-6 mb-6"
    >
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Processing Controls</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Start From Acronym
          </label>
          <input
            type="text"
            value={settings.startFromAcronym}
            onChange={(e) => setSettings({ ...settings, startFromAcronym: e.target.value })}
            placeholder="e.g., AVWSS"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Grade
          </label>
          <input
            type="number"
            min="1"
            max="5"
            value={settings.grade}
            onChange={(e) => setSettings({ ...settings, grade: parseInt(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Batch Size
          </label>
          <input
            type="number"
            min="1"
            value={settings.batchSize}
            onChange={(e) => setSettings({ ...settings, batchSize: parseInt(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={isProcessing}
          className={`w-full py-2 px-4 rounded-md text-white font-medium ${
            isProcessing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          }`}
        >
          {isProcessing ? 'Processing...' : 'Start Processing'}
        </motion.button>
      </form>
    </motion.div>
  );
};

export default ProcessingControls; 
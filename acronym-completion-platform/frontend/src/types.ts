export interface Result {
  id: string;
  acronym: string;
  definition: string;
  description: string;
  tags: string[];
  grade: number;
  metadata: Record<string, string>;
}

export interface ProcessingConfig {
  batchSize: number;
  gradeFilter: {
    enabled: boolean;
    singleGrade?: string;
    gradeRange?: {
      start: string;
      end: string;
    };
  };
  enrichment: {
    enabled: boolean;
    addMissingDefinitions?: boolean;
    generateDescriptions?: boolean;
    suggestTags?: boolean;
    useWebSearch?: boolean;
    useInternalKb?: boolean;
  };
  startingPoint: {
    enabled: boolean;
    acronym?: string;
  };
  rateLimiting?: {
    enabled: boolean;
    requestsPerSecond: number;
    burstSize: number;
    maxRetries: number;
  };
  outputFormat?: {
    includeDefinitions: boolean;
    includeDescriptions: boolean;
    includeTags: boolean;
    includeGrade: boolean;
    includeMetadata: boolean;
  };
  caching?: {
    enabled: boolean;
    ttlSeconds: number;
  };
}

export interface SettingsState {
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
  isOpen?: boolean;
  startingPoint?: string;
}

export interface FileUploadProps {
  label: string;
  onFileUpload: (file: File) => void;
  fileName?: string | null;
}

export interface ProcessingStatusProps {
  templateFile: string | null;
  acronymsFile: string | null;
  isProcessing: boolean;
  progress: number;
  error: string | null;
}

export interface ResultsProps {
  results: Result[];
  onUpdateAcronym?: (result: Result) => void;
}

export interface HistoryProps {
  onSelectHistory: (history: Result[]) => void;
  onDeleteHistory: (id: string) => void;
} 
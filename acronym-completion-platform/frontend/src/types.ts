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
    singleGrade: number | null;
    gradeRange: [number, number] | null;
  };
  enrichment: {
    enabled: boolean;
    addMissingDefinitions: boolean;
    generateDescriptions: boolean;
    suggestTags: boolean;
    useWebSearch: boolean;
    useInternalKb: boolean;
  };
  startingPoint: {
    enabled: boolean;
    acronym: string | null;
  };
  rateLimiting: {
    enabled: boolean;
    requestsPerMinute: number;
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

export interface SettingsState {
  geminiApiKeys: string[];
  processingConfig: {
    batchSize: number;
    gradeFilter: {
      enabled: boolean;
      singleGrade: number | null;
      gradeRange: [number, number] | null;
    };
    enrichment: {
      enabled: boolean;
      addMissingDefinitions: boolean;
      generateDescriptions: boolean;
      suggestTags: boolean;
      useWebSearch: boolean;
      useInternalKb: boolean;
    };
    startingPoint: {
      enabled: boolean;
      acronym: string | null;
    };
    rateLimiting: {
      enabled: boolean;
      requestsPerMinute: number;
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
  };
  autoSave: boolean;
  historyLimit: number;
  theme: 'light' | 'dark';
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

export interface Settings {
  geminiApiKeys: string[];
  processingConfig: {
    batchSize: number;
    gradeFilter: {
      enabled: boolean;
      singleGrade: number | null;
      gradeRange: [number, number] | null;
    };
    enrichment: {
      enabled: boolean;
      addMissingDefinitions: boolean;
      generateDescriptions: boolean;
      suggestTags: boolean;
      useWebSearch: boolean;
      useInternalKb: boolean;
    };
    startingPoint: {
      enabled: boolean;
      acronym: string | null;
    };
    rateLimiting: {
      enabled: boolean;
      requestsPerMinute: number;
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
  };
} 
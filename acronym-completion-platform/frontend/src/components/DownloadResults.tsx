import { motion } from 'framer-motion';

interface Result {
  acronym: string;
  definition: string;
  description: string;
  tags: string;
  grade: string;
}

interface DownloadResultsProps {
  results: Result[];
  filename?: string;
}

export function DownloadResults({ results, filename = 'acronyms.csv' }: DownloadResultsProps) {
  const handleDownload = () => {
    if (results.length === 0) {
      return;
    }

    // Create CSV content
    const headers = ['Acronym', 'Definition', 'Description', 'Tags', 'Grade'];
    const csvContent = [
      headers.join(','),
      ...results.map(result => [
        result.acronym,
        result.definition,
        result.description,
        result.tags,
        result.grade
      ].join(','))
    ].join('\n');

    // Create blob and download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    // Set download attributes
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    // Append to document, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="mt-6">
      <button
        onClick={handleDownload}
        disabled={results.length === 0}
        className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg text-sm font-medium text-white transition-all duration-200 ${
          results.length === 0
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
        }`}
      >
        <svg
          className="h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
        <span>Download Results ({results.length} acronyms)</span>
      </button>
    </div>
  );
} 
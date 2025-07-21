import { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { parserApi } from '../services/api';
import { useNotifications } from '../components/NotificationProvider';
import { cn } from '../utils';
import type { ParseResult } from '../types';

export default function FileParser() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [parsing, setParsing] = useState(false);
  const [result, setResult] = useState<ParseResult | null>(null);
  const { addNotification } = useNotifications();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
    }
  };

  const handleParse = async () => {
    if (!selectedFile) {
      addNotification({
        type: 'error',
        title: 'No file selected',
        message: 'Please select a file to parse.',
      });
      return;
    }

    setParsing(true);
    try {
      const uploadResult = await parserApi.uploadFiles([selectedFile]);
      setResult(uploadResult.results[0]); // Get first result
      addNotification({
        type: 'success',
        title: 'File parsed successfully',
        message: `Processed ${selectedFile.name}`,
      });
    } catch (error) {
      console.error('Failed to parse file:', error);
      addNotification({
        type: 'error',
        title: 'Failed to parse file',
        message: 'An error occurred while parsing the file. Please try again.',
      });
    } finally {
      setParsing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">File Parser</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload and parse V93K test files to extract relevant information
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Test File</h3>
          
          <div className="space-y-4">
            {/* File Input */}
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-10 h-10 mb-3 text-gray-400" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">
                    V93K test files (.txt, .log, .csv)
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileSelect}
                  accept=".txt,.log,.csv"
                />
              </label>
            </div>

            {/* Selected File Info */}
            {selectedFile && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-blue-400 mr-3" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-900">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-blue-700">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Parse Button */}
            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleParse}
                disabled={!selectedFile || parsing}
                className={cn(
                  "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white",
                  selectedFile && !parsing
                    ? "bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    : "bg-gray-400 cursor-not-allowed"
                )}
              >
                {parsing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Parsing...
                  </>
                ) : (
                  'Parse File'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <div className="flex items-center mb-4">
              <CheckCircle className="w-6 h-6 text-green-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Parse Results</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{result.error_count + result.warning_count}</div>
                <div className="text-sm text-gray-500">Total Issues</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{result.error_count}</div>
                <div className="text-sm text-gray-500">Errors</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{result.file_type}</div>
                <div className="text-sm text-gray-500">File Type</div>
              </div>
            </div>

            {/* File Info */}
            <div className="mb-6">
              <h4 className="text-md font-medium text-gray-900 mb-2">File Information</h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Filename</dt>
                    <dd className="text-sm text-gray-900">{result.filename}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">File Type</dt>
                    <dd className="text-sm text-gray-900">{result.file_type}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Parsing Status</dt>
                    <dd className="text-sm text-gray-900">
                      {result.parsing_successful ? 'Successful' : 'Failed'}
                    </dd>
                  </div>
                  {result.module_name && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Module Name</dt>
                      <dd className="text-sm text-gray-900">{result.module_name}</dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>

            {/* Test Results Preview */}
            {result.test_results && Array.isArray(result.test_results) && result.test_results.length > 0 && (
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-2">
                  Test Results Preview ({result.test_results.length} items)
                </h4>
                <div className="max-h-96 overflow-y-auto">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                      {JSON.stringify(result.test_results, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {/* Errors */}
            {result.errors && result.errors.length > 0 && (
              <div className="mt-6">
                <h4 className="text-md font-medium text-gray-900 mb-2 flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                  Parse Errors ({result.errors.length})
                </h4>
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <ul className="space-y-1">
                    {result.errors.map((error, index) => (
                      <li key={index} className="text-sm text-red-800">
                        {error.message}
                        {error.line_number && (
                          <span className="text-red-600 ml-2">(Line {error.line_number})</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

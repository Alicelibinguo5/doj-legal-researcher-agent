import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AnalysisForm from './components/AnalysisForm';
import ProgressIndicator from './components/ProgressIndicator';
import StatsCards from './components/StatsCards';
import ChargesChart from './components/ChargesChart';
import CasesTable from './components/CasesTable';
import { analyzeCases, pollJobStatus } from './utils/api';

const LOCAL_STORAGE_KEY = 'doj_research_last_results';

function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const [analysisStartTime, setAnalysisStartTime] = useState(null);
  const [analysisEndTime, setAnalysisEndTime] = useState(null);

  // Load last results from localStorage on mount
  useEffect(() => {
    const lastResults = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (lastResults) {
      try {
        const parsed = JSON.parse(lastResults);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setResults(parsed);
          setStatus('done');
        }
      } catch (e) {
        // Ignore parse errors
      }
    }
  }, []);

  // Save results to localStorage after analysis
  useEffect(() => {
    if (results && results.length > 0 && status === 'done') {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(results));
    }
  }, [results, status]);

  const handleStartAnalysis = async (formData) => {
    setIsLoading(true);
    setStatus('pending');
    setError(null);
    setResults([]);
    setProgress(null);
    setAnalysisStartTime(Date.now());
    setAnalysisEndTime(null);

    try {
      // Start the analysis
      const response = await analyzeCases(formData);
      const jobId = response.job_id;

      if (!jobId) {
        throw new Error('No job ID returned from server');
      }

      // Poll for results
      const analysisResults = await pollJobStatus(jobId, (jobData) => {
        setStatus(jobData.status);
        if (jobData.progress) {
          setProgress(jobData.progress);
        }
        if (jobData.error) {
          setError(jobData.error);
        }
      });

      setResults(analysisResults || []);
      setStatus('done');
      setAnalysisEndTime(Date.now());
      
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err.message);
      setStatus('error');
      setAnalysisEndTime(Date.now());
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate execution time in seconds
  let executionTime = null;
  if (analysisStartTime && analysisEndTime) {
    executionTime = Math.round((analysisEndTime - analysisStartTime) / 1000);
  }

  // Format execution time as mm:ss
  const formatExecutionTime = (seconds) => {
    if (seconds == null) return '';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Analysis Form */}
          <AnalysisForm 
            onStartAnalysis={handleStartAnalysis}
            isLoading={isLoading}
          />

          {/* Progress Indicator */}
          {status && status !== 'done' && (
            <ProgressIndicator 
              status={status}
              progress={progress}
              error={error}
            />
          )}

          {/* Results Section */}
          {results.length > 0 && status === 'done' && (
            <>
              {/* Summary Statistics */}
              <StatsCards results={results} />

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <ChargesChart results={results} />
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Summary</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Cases Analyzed:</span>
                      <span className="font-medium">{results.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Analysis Date:</span>
                      <span className="font-medium">{new Date().toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Execution Time:</span>
                      <span className="font-medium">{formatExecutionTime(executionTime)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Cases Table */}
              <CasesTable results={results} />
            </>
          )}

          {/* Empty State */}
          {!isLoading && (!status || (status === 'done' && results.length === 0)) && (
            <div className="card text-center py-12">
              <div className="max-w-md mx-auto">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Analyze</h3>
                <p className="text-gray-600 mb-6">
                  Configure your analysis parameters above and click "Start Analysis" to begin processing DOJ press releases.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App; 
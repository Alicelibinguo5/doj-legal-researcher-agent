import React from 'react';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const ProgressIndicator = ({ status, progress, error }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />;
      case 'done':
        return <CheckCircle className="w-6 h-6 text-success-600" />;
      case 'error':
        return <AlertCircle className="w-6 h-6 text-danger-600" />;
      default:
        return <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Analyzing cases...';
      case 'done':
        return 'Analysis complete!';
      case 'error':
        return 'Analysis failed';
      default:
        return 'Initializing...';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'text-primary-600';
      case 'done':
        return 'text-success-600';
      case 'error':
        return 'text-danger-600';
      default:
        return 'text-gray-600';
    }
  };

  if (!status) return null;

  return (
    <div className="card">
      <div className="flex items-center space-x-4">
        {getStatusIcon()}
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${getStatusColor()}`}>
            {getStatusText()}
          </h3>
          {progress && (
            <div className="mt-2">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Progress</span>
                <span>{progress.current || 0} / {progress.total || '?'}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ 
                    width: progress.total ? `${(progress.current / progress.total) * 100}%` : '0%' 
                  }}
                ></div>
              </div>
            </div>
          )}
          {error && (
            <p className="text-sm text-danger-600 mt-2">
              Error: {error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator; 
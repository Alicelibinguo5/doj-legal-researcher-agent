import React, { useState } from 'react';
import { Play, Settings } from 'lucide-react';

const AnalysisForm = ({ onStartAnalysis, isLoading }) => {
  const [formData, setFormData] = useState({
    fraudType: 'Any',
    maxPages: 100,  // Raised from 10 to 100
    maxCases: 1000  // Raised from 10 to 1000
  });

  const fraudTypes = [
    { value: 'Any', label: 'Any Type' },
    { value: 'financial_fraud', label: 'Financial Fraud' },
    { value: 'health_care_fraud', label: 'Healthcare Fraud' },
    { value: 'disaster_fraud', label: 'Disaster Fraud' },
    { value: 'consumer_protection', label: 'Consumer Protection' },
    { value: 'cybercrime', label: 'Cybercrime' },
    { value: 'false_claims_act', label: 'False Claims Act' },
    { value: 'public_corruption', label: 'Public Corruption' },
    { value: 'tax', label: 'Tax Fraud' },
    { value: 'immigration', label: 'Immigration Fraud' },
    { value: 'intellectual_property', label: 'Intellectual Property' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartAnalysis(formData);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <Settings className="w-5 h-5 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">Analysis Configuration</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Fraud Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fraud Type
            </label>
            <select
              value={formData.fraudType}
              onChange={(e) => handleChange('fraudType', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {fraudTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Max Pages */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Pages: {formData.maxPages}
            </label>
            <input
              type="range"
              min="1"
              max="100"
              value={formData.maxPages}
              onChange={(e) => handleChange('maxPages', parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>100</span>
            </div>
          </div>

          {/* Max Cases */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Cases: {formData.maxCases}
            </label>
            <input
              type="range"
              min="1"
              max="1000"  // Raised from 100 to 1000
              value={formData.maxCases}
              onChange={(e) => handleChange('maxCases', parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>1000</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Start Analysis</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AnalysisForm; 
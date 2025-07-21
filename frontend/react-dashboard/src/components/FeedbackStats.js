import React, { useState, useEffect } from 'react';
import { BarChart3, Download, TrendingUp, TrendingDown, MessageSquare } from 'lucide-react';
import { getFeedbackStats, exportTrainingData } from '../utils/api';

const FeedbackStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadFeedbackStats();
  }, []);

  const loadFeedbackStats = async () => {
    try {
      setLoading(true);
      const data = await getFeedbackStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Failed to load feedback statistics');
      console.error('Error loading feedback stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportTrainingData = async () => {
    try {
      setExporting(true);
      const result = await exportTrainingData();
      if (result.success) {
        alert('Training data exported successfully!');
      } else {
        alert('Failed to export training data: ' + result.message);
      }
    } catch (err) {
      alert('Error exporting training data: ' + err.message);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feedback Statistics</h3>
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feedback Statistics</h3>
        <div className="text-red-600">{error}</div>
        <button 
          onClick={loadFeedbackStats}
          className="mt-2 px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!stats || stats.total_feedback === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feedback Statistics</h3>
        <div className="text-gray-600">No feedback data available yet.</div>
      </div>
    );
  }

  const positiveRate = ((stats.positive_feedback / stats.total_feedback) * 100).toFixed(1);
  const negativeRate = ((stats.negative_feedback / stats.total_feedback) * 100).toFixed(1);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Feedback Statistics</h3>
        <button
          onClick={handleExportTrainingData}
          disabled={exporting}
          className="flex items-center px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50"
        >
          <Download className="w-4 h-4 mr-1" />
          {exporting ? 'Exporting...' : 'Export Training Data'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-blue-900">{stats.total_feedback}</div>
              <div className="text-sm text-blue-700">Total Feedback</div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-green-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-green-900">{stats.positive_feedback}</div>
              <div className="text-sm text-green-700">Positive ({positiveRate}%)</div>
            </div>
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingDown className="w-8 h-8 text-red-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-red-900">{stats.negative_feedback}</div>
              <div className="text-sm text-red-700">Negative ({negativeRate}%)</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-center">
            <MessageSquare className="w-8 h-8 text-gray-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.neutral_feedback}</div>
              <div className="text-sm text-gray-700">Comments</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Model Performance Insights</h4>
        <div className="text-sm text-gray-700 space-y-1">
          <div>• Positive feedback rate: <span className="font-medium">{positiveRate}%</span></div>
          <div>• Negative feedback rate: <span className="font-medium">{negativeRate}%</span></div>
          {stats.total_feedback > 10 && (
            <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
              <div className="text-yellow-800 text-xs">
                💡 Tip: With {stats.total_feedback} feedback points, consider retraining the model 
                to improve accuracy based on user feedback.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackStats; 
import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, MessageSquare, CheckCircle, XCircle } from 'lucide-react';
import { submitFeedback } from '../utils/api';

const FeedbackWidget = ({ caseData, onFeedbackSubmitted }) => {
  const [feedback, setFeedback] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showTextInput, setShowTextInput] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleFeedback = async (feedbackType) => {
    if (submitted) return;
    
    setFeedback(feedbackType);
    
    if (feedbackType === 'neutral') {
      setShowTextInput(true);
    } else {
      await submitFeedbackToAPI(feedbackType);
    }
  };

  const submitFeedbackToAPI = async (feedbackType) => {
    setIsSubmitting(true);
    
    try {
      const feedbackData = {
        case_id: caseData.url || caseData.title, // Use URL or title as case ID
        url: caseData.url || '',
        user_feedback: feedbackType,
        feedback_text: feedbackText || null,
        model_prediction: {
          fraud_flag: caseData.fraud_flag || false,
          money_laundering_flag: caseData.money_laundering_flag || false,
          charges: caseData.charges || [],
          charge_categories: caseData.charge_categories || []
        },
        confidence_score: 0.8 // Default confidence score
      };

      const result = await submitFeedback(feedbackData);
      
      if (result.success) {
        setSubmitted(true);
        if (onFeedbackSubmitted) {
          onFeedbackSubmitted(feedbackType, result.feedback_id);
        }
      } else {
        console.error('Feedback submission failed:', result.message);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!feedbackText.trim()) return;
    await submitFeedbackToAPI('neutral');
  };

  if (submitted) {
    return (
      <div className="flex items-center justify-center p-2 bg-green-50 border border-green-200 rounded-lg">
        <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
        <span className="text-sm text-green-700">Feedback submitted!</span>
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg p-3 bg-white">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">Was this analysis helpful?</span>
        {isSubmitting && (
          <div className="text-xs text-gray-500">Submitting...</div>
        )}
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handleFeedback('positive')}
          disabled={isSubmitting || submitted}
          className={`flex items-center px-3 py-1 rounded-md text-sm transition-colors ${
            feedback === 'positive'
              ? 'bg-green-100 text-green-700 border border-green-300'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
          } ${isSubmitting || submitted ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <ThumbsUp className="w-4 h-4 mr-1" />
          Yes
        </button>
        
        <button
          onClick={() => handleFeedback('negative')}
          disabled={isSubmitting || submitted}
          className={`flex items-center px-3 py-1 rounded-md text-sm transition-colors ${
            feedback === 'negative'
              ? 'bg-red-100 text-red-700 border border-red-300'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
          } ${isSubmitting || submitted ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <ThumbsDown className="w-4 h-4 mr-1" />
          No
        </button>
        
        <button
          onClick={() => handleFeedback('neutral')}
          disabled={isSubmitting || submitted}
          className={`flex items-center px-3 py-1 rounded-md text-sm transition-colors ${
            feedback === 'neutral'
              ? 'bg-blue-100 text-blue-700 border border-blue-300'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
          } ${isSubmitting || submitted ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <MessageSquare className="w-4 h-4 mr-1" />
          Comment
        </button>
      </div>
      
      {showTextInput && (
        <div className="mt-3">
          <textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="Please provide additional feedback..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="3"
          />
          <div className="flex items-center justify-end space-x-2 mt-2">
            <button
              onClick={() => {
                setShowTextInput(false);
                setFeedbackText('');
                setFeedback(null);
              }}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={handleTextSubmit}
              disabled={!feedbackText.trim() || isSubmitting}
              className={`px-3 py-1 rounded-md text-sm ${
                feedbackText.trim() && !isSubmitting
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              Submit
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackWidget; 
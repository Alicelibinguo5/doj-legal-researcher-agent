import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Analysis functions
export const analyzeCases = async (params) => {
  try {
    console.log('🚀 Starting analysis with params:', params);
    console.log('📡 Making POST request to:', `${API_BASE_URL}/analyze/`);
    
    const response = await axios.post(`${API_BASE_URL}/analyze/`, params);
    console.log('✅ Analysis started successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error starting analysis:', error);
    throw error;
  }
};

export const getJobStatus = async (jobId) => {
  try {
    console.log('📊 Checking job status for:', jobId);
    const response = await axios.get(`${API_BASE_URL}/job/${jobId}`);
    console.log('📊 Job status received:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Error getting job status:', error);
    throw error;
  }
};

export const pollJobStatus = async (jobId, onUpdate) => {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getJobStatus(jobId);
        onUpdate(status);
        
        if (status.status === 'done') {
          resolve(status.result || []);
        } else if (status.status === 'error') {
          reject(new Error(status.error || 'Job failed'));
        } else {
          // Continue polling
          setTimeout(poll, 2000);
        }
      } catch (error) {
        console.error('Error polling job status:', error);
        reject(error);
      }
    };
    
    poll();
  });
};

// Feedback functions
export const submitFeedback = async (feedbackData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/feedback/`, feedbackData);
    return response.data;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
};

export const getFeedbackStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/feedback/stats`);
    return response.data;
  } catch (error) {
    console.error('Error getting feedback stats:', error);
    throw error;
  }
};

export const getCaseFeedback = async (caseId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/feedback/case/${caseId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting case feedback:', error);
    throw error;
  }
};

export const exportTrainingData = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/feedback/export`);
    return response.data;
  } catch (error) {
    console.error('Error exporting training data:', error);
    throw error;
  }
}; 
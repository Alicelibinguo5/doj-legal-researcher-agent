import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const analyzeCases = async (params) => {
  try {
    const response = await api.post('/analyze/', {
      max_pages: params.maxPages,
      max_cases: params.maxCases,
      fraud_type: params.fraudType === 'Any' ? null : params.fraudType
    });
    return response.data;
  } catch (error) {
    throw new Error(`Analysis failed: ${error.response?.data?.detail || error.message}`);
  }
};

export const getJobStatus = async (jobId) => {
  try {
    const response = await api.get(`/job/${jobId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get job status: ${error.response?.data?.detail || error.message}`);
  }
};

export const pollJobStatus = async (jobId, onProgress) => {
  const maxAttempts = 60; // 2 minutes with 2-second intervals
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    try {
      const jobData = await getJobStatus(jobId);
      
      if (onProgress) {
        onProgress(jobData);
      }
      
      if (jobData.status === 'done') {
        return jobData.result;
      }
      
      if (jobData.status === 'error') {
        throw new Error(jobData.error || 'Job failed');
      }
      
      // Wait 2 seconds before next poll
      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
      
    } catch (error) {
      throw error;
    }
  }
  
  throw new Error('Job polling timed out');
}; 
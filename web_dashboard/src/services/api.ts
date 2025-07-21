import axios, { AxiosResponse } from 'axios';
import { 
  SystemHealth, 
  ClassificationResult, 
  RecommendationResult, 
  UploadResult, 
  UsageStats, 
  PerformanceMetrics, 
  IssueAnalytics,
  Solution 
} from '@/types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// System API
export const systemApi = {
  getHealth: async (): Promise<SystemHealth> => {
    const response: AxiosResponse<SystemHealth> = await api.get('/system/health');
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/system/status');
    return response.data;
  },

  getConfig: async () => {
    const response = await api.get('/system/config');
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/system/metrics');
    return response.data;
  },

  initialize: async (components: string[] = ['database', 'classifier', 'recommender']) => {
    const formData = new FormData();
    components.forEach(component => {
      formData.append('components', component);
    });
    const response = await api.post('/system/initialize', formData);
    return response.data;
  },
};

// Parser API
export const parserApi = {
  uploadFiles: async (files: File[], moduleId?: string, baselineVersion?: string): Promise<UploadResult> => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    if (moduleId) {
      formData.append('module_name', moduleId);
    }
    if (baselineVersion) {
      formData.append('baseline_version', baselineVersion);
    }

    const response: AxiosResponse<UploadResult> = await api.post('/parser/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  parseDirectory: async (directoryPath: string, recursive: boolean = true, moduleId?: string, baselineVersion?: string) => {
    const formData = new FormData();
    formData.append('directory_path', directoryPath);
    formData.append('recursive', recursive.toString());
    if (moduleId) {
      formData.append('module_name', moduleId);
    }
    if (baselineVersion) {
      formData.append('baseline_version', baselineVersion);
    }

    const response = await api.post('/parser/parse-directory', formData);
    return response.data;
  },

  getSupportedFormats: async () => {
    const response = await api.get('/parser/supported-formats');
    return response.data;
  },
};

// Classifier API
export const classifierApi = {
  classify: async (text: string, includeConfidence: boolean = true, topN: number = 3): Promise<ClassificationResult> => {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('include_confidence', includeConfidence.toString());
    formData.append('top_n', topN.toString());

    const response: AxiosResponse<ClassificationResult> = await api.post('/classifier/classify', formData);
    return response.data;
  },

  classifyBatch: async (texts: string[], includeConfidence: boolean = true, topN: number = 1) => {
    const formData = new FormData();
    texts.forEach(text => {
      formData.append('texts', text);
    });
    formData.append('include_confidence', includeConfidence.toString());
    formData.append('top_n', topN.toString());

    const response = await api.post('/classifier/classify-batch', formData);
    return response.data;
  },

  classifyFromFile: async (fileData: any, extractErrors: boolean = true, extractWarnings: boolean = false) => {
    const response = await api.post('/classifier/classify-from-file', {
      file_data: fileData,
      extract_errors: extractErrors,
      extract_warnings: extractWarnings,
      include_metadata: true,
    });
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/classifier/categories');
    return response.data;
  },

  getModelStats: async () => {
    const response = await api.get('/classifier/model-stats');
    return response.data;
  },
};

// Recommender API
export const recommenderApi = {
  getRecommendations: async (
    issueText: string, 
    topK: number = 5, 
    minSimilarity: number = 0.1, 
    includeDetails: boolean = true
  ): Promise<RecommendationResult> => {
    const formData = new FormData();
    formData.append('issue_text', issueText);
    formData.append('top_k', topK.toString());
    formData.append('min_similarity', minSimilarity.toString());
    formData.append('include_details', includeDetails.toString());

    const response: AxiosResponse<RecommendationResult> = await api.post('/recommender/recommend', formData);
    return response.data;
  },

  getRecommendationsByCategory: async (issueText: string, category: string, topK: number = 5, minSimilarity: number = 0.1) => {
    const formData = new FormData();
    formData.append('issue_text', issueText);
    formData.append('category', category);
    formData.append('top_k', topK.toString());
    formData.append('min_similarity', minSimilarity.toString());

    const response = await api.post('/recommender/recommend-for-category', formData);
    return response.data;
  },

  getBatchRecommendations: async (issues: string[], topK: number = 3, minSimilarity: number = 0.1) => {
    const formData = new FormData();
    issues.forEach(issue => {
      formData.append('issues', issue);
    });
    formData.append('top_k', topK.toString());
    formData.append('min_similarity', minSimilarity.toString());

    const response = await api.post('/recommender/batch-recommend', formData);
    return response.data;
  },

  browseSolutions: async (category?: string, searchTerm?: string, limit: number = 20, offset: number = 0): Promise<{ solutions: Solution[], total_solutions: number }> => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (searchTerm) params.append('search_term', searchTerm);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await api.get(`/recommender/solutions?${params}`);
    return response.data;
  },

  getSolutionDetails: async (solutionId: string) => {
    const response = await api.get(`/recommender/solution/${solutionId}`);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/recommender/stats');
    return response.data;
  },
};

// Monitoring API
export const monitoringApi = {
  getUsageStats: async (days: number = 7, includeDetails: boolean = true): Promise<UsageStats> => {
    const params = new URLSearchParams();
    params.append('days', days.toString());
    params.append('include_details', includeDetails.toString());

    const response: AxiosResponse<UsageStats> = await api.get(`/monitoring/usage-stats?${params}`);
    return response.data;
  },

  getPerformanceMetrics: async (component?: string, hours: number = 24): Promise<PerformanceMetrics> => {
    const params = new URLSearchParams();
    if (component) params.append('component', component);
    params.append('hours', hours.toString());

    const response: AxiosResponse<PerformanceMetrics> = await api.get(`/monitoring/performance-metrics?${params}`);
    return response.data;
  },

  getIssueAnalytics: async (days: number = 30, category?: string): Promise<IssueAnalytics> => {
    const params = new URLSearchParams();
    params.append('days', days.toString());
    if (category) params.append('category', category);

    const response: AxiosResponse<IssueAnalytics> = await api.get(`/monitoring/issue-analytics?${params}`);
    return response.data;
  },

  getSolutionAnalytics: async (days: number = 30) => {
    const params = new URLSearchParams();
    params.append('days', days.toString());

    const response = await api.get(`/monitoring/solution-analytics?${params}`);
    return response.data;
  },

  getSystemAlerts: async (severity?: string, hours: number = 24, resolved?: boolean) => {
    const params = new URLSearchParams();
    if (severity) params.append('severity', severity);
    params.append('hours', hours.toString());
    if (resolved !== undefined) params.append('resolved', resolved.toString());

    const response = await api.get(`/monitoring/system-alerts?${params}`);
    return response.data;
  },

  getSummaryReport: async (days: number = 7) => {
    const params = new URLSearchParams();
    params.append('days', days.toString());

    const response = await api.get(`/monitoring/reports/summary?${params}`);
    return response.data;
  },
};

export default api;

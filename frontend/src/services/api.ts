import axios from 'axios';
import { User, Email, EmailSummary, EmailFetchParams, EmailFilters } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  getGoogleAuthUrl: async () => {
    const response = await api.get('/auth/google');
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await api.delete('/auth/logout');
    localStorage.removeItem('auth_token');
    return response.data;
  },
};

// Gmail API
export const gmailApi = {
  syncEmails: async (options: { incremental?: boolean; maxResults?: number; batchSize?: number; onlyInbox?: boolean; labels?: string[] } = {}) => {
    const response = await api.post('/gmail/sync', {
      incremental: options.incremental ?? true,
      max_results: options.maxResults ?? null,
      batch_size: options.batchSize ?? 100,
      only_inbox: options.onlyInbox ?? true,
      labels: options.labels ?? null,
    });
    return response.data;
  },

  getEmails: async (params: EmailFetchParams = {}): Promise<Email[]> => {
    const response = await api.get('/gmail/emails', { params });
    return response.data.emails || [];
  },
};

// AI API
export const aiApi = {
  classifyEmails: async () => {
    const response = await api.post('/ai/classify');
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get('/ai/categories');
    return response.data;
  },

  getSpamEmails: async (): Promise<Email[]> => {
    const response = await api.get('/ai/spam');
    return response.data.emails || [];
  },

  deleteSpamEmails: async () => {
    const response = await api.delete('/ai/spam');
    return response.data;
  },

  bulkDeleteEmails: async (emailIds: string[], permanent: boolean = false) => {
    const response = await api.post('/ai/bulk/delete', {
      email_ids: emailIds,
      permanent,
    });
    return response.data;
  },
};

// Chat API
export const chatApi = {
  sendMessage: async (message: string, context?: any[]) => {
    const response = await api.post('/chat/chat', {
      message,
      context,
    });
    return response.data;
  },

  getSummary: async (): Promise<EmailSummary> => {
    const response = await api.get('/chat/summary');
    return response.data;
  },

  getSuggestions: async () => {
    const response = await api.get('/chat/suggestions');
    return response.data;
  },

  searchEmails: async (
    query: string,
    filters: EmailFilters = {},
    limit: number = 20
  ): Promise<Email[]> => {
    const response = await api.post('/chat/search', {
      query,
      ...filters,
      limit,
    });
    return response.data.results || [];
  },

  getQuickActions: async () => {
    const response = await api.get('/chat/quick-actions');
    return response.data;
  },
};

// Analytics API
export const analyticsApi = {
  getOverview: async (days: number = 7) => {
    const tzOffset = new Date().getTimezoneOffset();
    const response = await api.get(`/analytics/overview?days=${days}&tz_offset=${tzOffset}`);
    return response.data;
  },

  getTrends: async (period: string = '30d') => {
    const response = await api.get(`/analytics/trends?period=${period}`);
    return response.data;
  },
};

export default api;
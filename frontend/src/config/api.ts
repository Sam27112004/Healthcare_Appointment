import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor - attach JWT
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

import { toast } from '../hooks/use-toast';

// Response interceptor - handle 401 & Global Error Toast
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Show toast for error
    const detail = error.response?.data?.detail;
    
    // Check if it's an array of pydantic errors or just a string
    let message = 'An unexpected error occurred';
    if (typeof detail === 'string') {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail[0]?.msg || 'Validation Error';
    }

    if (error.response?.status && error.response.status >= 400 && error.response.status !== 401) {
      toast({
        variant: "destructive",
        title: "Error",
        description: message,
      });
    }

    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

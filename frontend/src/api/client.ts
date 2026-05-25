import axios from 'axios';

export const api = axios.create({ baseURL: '/api' });

export const setToken = (t: string) => {
  api.defaults.headers.common['Authorization'] = `Bearer ${t}`;
  localStorage.setItem('token', t);
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

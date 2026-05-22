import axios from 'axios';
export const api = axios.create({ baseURL: '/api' });
export const setToken = (t: string) => { api.defaults.headers.common['Authorization'] = `Bearer ${t}`; localStorage.setItem('token', t); };

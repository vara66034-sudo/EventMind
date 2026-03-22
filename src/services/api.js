import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_ODOO_URL || 'http://localhost:8069';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 10000,
});

// Хуйня для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API для событий
export const eventsAPI = {
  // Получение всех событий
  getAll: (params = {}) => {
    return api.get('/api/events', { params });
  },
  
  // Получение 1 события по ID
  getById: (id) => {
    return api.get(`/api/events/${id}`);
  },
  
  // Регистрация на событие
  register: (eventId, userData) => {
    return api.post(`/api/events/${eventId}/register`, userData);
  },
  
  // Получение .ics файл
  getIcs: async (id) => {
    const response = await api.get(`/event/${id}/ics`, {
      responseType: 'blob',
    });
    return response;
  },
  
  // Поиск событий
  search: (query, params = {}) => {
    return api.get('/api/events/search', {
      params: { q: query, ...params },
    });
  },
};

// API для уведомлений
export const notificationsAPI = {
  sendTest: (registrationId) => {
    return api.post('/api/notifications/test', {
      registration_id: registrationId,
    });
  },
  
  getStats: () => {
    return api.get('/api/notifications/stats');
  },
  
  subscribe: (email, eventId) => {
    return api.post('/api/notifications/subscribe', {
      email,
      event_id: eventId,
    });
  },
};

// API для городов
export const citiesAPI = {
  getAll: () => {
    return api.get('/api/cities');
  },
};

// API для авторизации
export const authAPI = {
  login: (email, password) => {
    return api.post('/api/auth/login', { email, password });
  },
  
  register: (userData) => {
    return api.post('/api/auth/register', userData);
  },
  
  logout: () => {
    return api.post('/api/auth/logout');
  },
  
  me: () => {
    return api.get('/api/auth/me');
  },
};

// API для пользователя
export const userAPI = {
  getProfile: () => {
    return api.get('/api/user/profile');
  },
  
  updateProfile: (data) => {
    return api.put('/api/user/profile', data);
  },
  
  myRegistrations: () => {
    return api.get('/api/user/registrations');
  },
};

export default api;
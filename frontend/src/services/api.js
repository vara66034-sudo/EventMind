import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://204.12.253.210:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

const sendAction = async (action, payload) => {
  const response = await api.post('/api/auth', {
    action,
    ...payload,
  });
  return response.data;
};

export const scheduleAPI = {
  getSchedule: async (userId, status = 'planned') => {
    return sendAction('get_schedule', { user_id: userId, status });
  },

  addToSchedule: async (userId, eventId) => {
    return sendAction('add_to_schedule', { user_id: userId, event_id: eventId });
  },

  removeFromSchedule: async (userId, eventId) => {
    return sendAction('remove_from_schedule', { user_id: userId, event_id: eventId });
  },

  getFavorites: async (userId) => {
    const response = await sendAction('get_favorites', { user_id: userId });
    return response.success ? response.data : [];
  },

  addToFavorites: async (userId, eventId) => {
    return sendAction('add_favorite', { user_id: userId, event_id: eventId });
  },

  removeFromFavorites: async (userId, eventId) => {
    return sendAction('remove_favorite', { user_id: userId, event_id: eventId });
  },

  addPlatformEvent: async (userId, eventId) => {
    return sendAction('add_platform_event', { user_id: userId, event_id: eventId });
  },

  addPersonalEvent: async (userId, title, start, end, description = '', location = '') => {
    return sendAction('add_personal_event', {
      user_id: userId,
      title,
      start: new Date(start).toISOString(),
      end: end ? new Date(end).toISOString() : null,
      description,
      location,
    });
  },

  updatePersonalEvent: async (userId, scheduleId, updates) => {
    return sendAction('update_personal_event', {
      user_id: userId,
      schedule_id: scheduleId,
      title: updates.title,
      start: updates.start ? new Date(updates.start).toISOString() : undefined,
      end: updates.end ? new Date(updates.end).toISOString() : undefined,
      description: updates.description,
      location: updates.location,
    });
  },

  removeEvent: async (userId, scheduleId) => {
    return sendAction('remove_event', { user_id: userId, schedule_id: scheduleId });
  },

  exportICS: async (userId) => {
    const response = await api.post('/api/auth', {
      action: 'export_ics',
      user_id: userId,
    }, { responseType: 'blob' });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'eventmind_schedule.ics');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export const eventsAPI = {
  getAll: async (params = {}) => {
    try {
      const result = await sendAction('get_events', params);
      
      if (result.success && result.data) {
        return result.data.items || [];
      }
      return [];
    } catch (error) {
      console.error('Error fetching events:', error);
      throw error;
    }
  },
  
  getById: async (id) => {
    const result = await sendAction('get_event', { event_id: id });
    return result.event || result.data || result;
  },
  
  register: async (eventId, userData) => 
    sendAction('register_for_event', { event_id: eventId, ...userData }),
    
  getIcs: async (id) => {
    const response = await api.post('/api/auth', {
      action: 'get_event_ics',
      event_id: id,
    }, { responseType: 'blob' });
    return response;
  },
  
  search: async (query, params = {}) => {
    const result = await sendAction('search_events', { q: query, ...params });
    return result.success ? (result.data.items || result.data) : [];
  },
  
  askAi: async (query) => {
    return sendAction('ask_ai', { question: query });
  },
};

export const notificationsAPI = {
  subscribe: (email, eventId) => 
    sendAction('subscribe_notification', { email, event_id: eventId }),
  sendTest: (registrationId) => 
    sendAction('send_test_notification', { registration_id: registrationId }),
  getStats: () => sendAction('get_notification_stats'),
};

export const citiesAPI = {
  getAll: () => sendAction('get_cities'),
};

export const authAPI = {
  register: async (userData) => {
    const { interests, ...rest } = userData;
    const payload = { ...rest };
    
    if (interests && Array.isArray(interests)) {
      payload.interests = interests;
    }
    
    return sendAction('register', payload);
  },
  
  login: async (email, password) => {
    return sendAction('login', { email, password });
  },
  
  logout: async (userId) => {
    return sendAction('logout', { user_id: userId });
  },
  
  me: async (userId) => {
    return sendAction('get_profile', { user_id: userId });
  },
};

export const userAPI = {
  getProfile: async (userId) => {
    return sendAction('get_profile', { user_id: userId });
  },
  
  updateProfile: async (userId, data) => {
    const { interests, ...rest } = data;
    const payload = { user_id: userId, ...rest };
    
    if (interests && Array.isArray(interests)) {
      payload.interests = interests;
    }
    
    return sendAction('update_interests', payload);
  },
  
  myRegistrations: async (userId) => {
    return sendAction('get_registrations', { user_id: userId });
  },
  
  getRecommendationsWithSchedule: async (userId) => {
    return sendAction('recommendations_with_schedule', { user_id: userId, limit: 10 });
  },
};

export default api;

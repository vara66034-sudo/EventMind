import axios from 'axios';

const API_URL = '';

// Получить токен (из localStorage или authAPI)
const getToken = () => localStorage.getItem('token');

// API для работы с расписанием
export const scheduleAPI = {
  
  // Получить расписание на неделю
  getSchedule: async (userId, startDate) => {
    const response = await axios.post(`${API_URL}/api/auth`, {
      action: 'get_schedule',
      user_id: userId,
      start_date: startDate.toISOString(),
      token: getToken(),
    });
    return response.data;
  },
  
  // Добавить занятый слот
  addBusySlot: async (userId, start, end, title) => {
    const response = await axios.post(`${API_URL}/api/auth`, {
      action: 'add_busy_slot',
      user_id: userId,
      start: start.toISOString(),
      end: end.toISOString(),
      title: title || 'Занят',
      token: getToken(),
    });
    return response.data;
  },
  
};

export default scheduleAPI;

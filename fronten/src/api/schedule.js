import { authAPI } from './auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const scheduleAPI = {
    // Получить расписание на неделю
    getSchedule: async (startDate) => {
        const token = authAPI.getToken();
        const user = authAPI.getCurrentUser();
        if (!user) throw new Error('User not authenticated');
        
        const response = await fetch(`${API_URL}/auth`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'get_schedule',
                user_id: user.user_id,
                start_date: startDate,
                token: token
            })
        });
        return response.json();
    },

    // Добавить занятый слот
    addBusySlot: async (start, end, title) => {
        const token = authAPI.getToken();
        const user = authAPI.getCurrentUser();
        if (!user) throw new Error('User not authenticated');
        
        const response = await fetch(`${API_URL}/auth`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'add_busy_slot',
                user_id: user.user_id,
                start: start,
                end: end,
                title: title,
                token: token
            })
        });
        return response.json();
    }
};

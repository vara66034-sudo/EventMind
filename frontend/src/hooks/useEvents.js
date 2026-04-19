import { useState, useEffect, useCallback } from 'react';
import { eventsAPI } from '../services/api';

export const useEvents = (filters = {}) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, total: 0 });

  const loadEvents = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      const response = await eventsAPI.getAll({ ...filters, page, limit: 20 });
      const data = response.data;

      const items = Array.isArray(data) ? data : (data.items || []);
      const total = data.total || items.length;
      
      setEvents(items);
      setPagination({ page, total });
    } catch (err) {
      console.error('Error loading events:', err);
      setError(err.message || 'Не удалось загрузить события');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadEvents(1);
  }, [loadEvents]);

  const refetch = useCallback(() => loadEvents(pagination.page), [loadEvents, pagination.page]);

  return { events, loading, error, pagination, refetch, loadPage: loadEvents };
};

export default useEvents;

import { useState, useEffect } from 'react';
import { eventsAPI } from '../services/api';

export const useEvents = (filters = {}) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadEvents();
  }, [filters]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await eventsAPI.getAll(filters);
      setEvents(response.data);
    } catch (err) {
      console.error('Error loading events:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { events, loading, error, refetch: loadEvents };
};

export default useEvents;
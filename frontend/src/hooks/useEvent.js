import { useState, useEffect, useCallback } from 'react';
import { eventsAPI } from '../services/api';

export const useEvent = (eventId) => {
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadEvent = useCallback(async () => {
    if (!eventId) return;
    try {
      setLoading(true);
      setError(null);
      const response = await eventsAPI.getById(eventId);
      setEvent(response);
    } catch (err) {
      console.error('Error loading event:', err);
      setError(err.message || 'Не удалось загрузить событие');
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    loadEvent();
  }, [loadEvent]);

  const refetch = useCallback(() => loadEvent(), [loadEvent]);

  return { event, loading, error, refetch };
};

export default useEvent;

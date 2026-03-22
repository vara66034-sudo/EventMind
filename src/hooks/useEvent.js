import { useState, useEffect } from 'react';
import { eventsAPI } from '../services/api';

export const useEvent = (eventId) => {
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (eventId) {
      loadEvent();
    }
  }, [eventId]);

  const loadEvent = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await eventsAPI.getById(eventId);
      setEvent(response.data);
    } catch (err) {
      console.error('Error loading event:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { event, loading, error, refetch: loadEvent };
};

export default useEvent;
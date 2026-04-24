import React, { useMemo, useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import EventCard from '../components/events/EventCard';
import Calendar from '../components/events/Calendar';
import Recommendations from '../components/events/Recommendations';
import useEvents from '../hooks/useEvents';
import { scheduleAPI } from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
`;

const EventsSection = styled.section`
  background: #522B5B;
  padding: 40px 0 60px 0;
  min-height: 60vh;
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  
  @media (max-width: 768px) {
    padding: 0 20px;
  }
`;

const EventsGrid = styled.div`
  display: flex;
  gap: 25px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding-bottom: 30px;
  
  &::-webkit-scrollbar {
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }
  
  &::-webkit-scrollbar-thumb {
    background: #854E6B;
    border-radius: 4px;
  }
  
  @media (max-width: 768px) {
    gap: 15px;
  }
`;

const InfoSection = styled.section`
  background: #FFFFFF;
  padding: 40px 0;
  color: #180018;
`;

const Loader = styled.div`
  text-align: center;
  padding: 60px;
  color: #FFFFFF;
  font-size: 20px;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 60px;
  color: #DFB6B2;
  font-size: 18px;
`;

const EventsPage = () => {
  const [selectedCity, setSelectedCity] = useState(null);
  const [favoriteIds, setFavoriteIds] = useState(new Set());

  const userId = useMemo(() => {
    const auth = localStorage.getItem('auth');
    return auth ? JSON.parse(auth).userId : null;
  }, []);

  const data = useMemo(() => ({
    city: selectedCity,
  }), [selectedCity]);
  
  const { events, loading, error, refetch } = useEvents(data);

  useEffect(() => {
    if (userId) {
      loadFavorites();
    }
  }, [userId]);

  const loadFavorites = async () => {
    if (!userId) return;
    try {
      const response = await scheduleAPI.getFavorites(userId);
      const data = Array.isArray(response) ? response : [];
      const ids = new Set(data.map(event => event.id));
      setFavoriteIds(ids);
    } catch (err) {
      console.error('Error loading favorites:', err);
      setFavoriteIds(new Set());
    }
  };

  const handleCitySelect = (city) => {
    setSelectedCity(city === 'Все города' ? null : city);
  };

  const handleAddToSchedule = useCallback(async (userId, eventId) => {
    if (!userId) return;
    try {
      await scheduleAPI.addPlatformEvent(userId, eventId);
      refetch();
    } catch (err) {
      console.error('Error adding to schedule:', err);
      alert('Не удалось добавить событие в расписание');
    }
  }, [refetch]);

  const handleToggleFavorite = useCallback(async (userId, eventId, shouldBeFavorite) => {
    if (!userId) return;
    try {
      if (shouldBeFavorite) {
        await scheduleAPI.addToFavorites(userId, eventId);
        setFavoriteIds(prev => new Set(prev).add(eventId));
      } else {
        await scheduleAPI.removeFromFavorites(userId, eventId);
        setFavoriteIds(prev => {
          const next = new Set(prev);
          next.delete(eventId);
          return next;
        });
      }
    } catch (err) {
      console.error('Error toggling favorite:', err);
      alert('Не удалось обновить избранное');
    }
  }, []);

  if (loading) {
    return (
      <PageContainer>
        <EventsSection>
          <ContentWrapper>
            <Loader>Загрузка событий...</Loader>
          </ContentWrapper>
        </EventsSection>
      </PageContainer>
    );
  }

  // Удаляем mockEvents и оставляем только реальные события
  const displayEvents = events || [];

  return (
    <PageContainer>
      <EventsSection>
        <ContentWrapper>
          <EventsGrid>
            {displayEvents.length > 0 ? (
              displayEvents.map((event) => (
                <EventCard 
                  key={event.id} 
                  event={event}
                  userId={userId}
                  onAddToSchedule={handleAddToSchedule}
                  onToggleFavorite={handleToggleFavorite}
                  isFavorite={favoriteIds.has(event.id)}
                />
              ))
            ) : (
              <ErrorMessage>События не найдены</ErrorMessage>
            )}
          </EventsGrid>
        </ContentWrapper>
      </EventsSection>

      <InfoSection>
        <ContentWrapper>
          <Calendar />
          <Recommendations />
        </ContentWrapper>
      </InfoSection>
    </PageContainer>
  );
};

export default EventsPage;

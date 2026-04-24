import React, { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Calendar from '../components/events/Calendar';
import Recommendations from '../components/events/Recommendations';
import { useEvent } from '../hooks/useEvent';
import { scheduleAPI } from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
`;

const EventHero = styled.section`
  background: #2B124C;
  padding: 40px 0;
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const EventCard = styled.div`
  background: #FBE4D8;
  border-radius: 24px;
  padding: 30px;
  margin-bottom: 30px;
`;

const EventImage = styled.div`
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #854E6B 0%, #512A59 100%);
  border-radius: 16px;
  margin-bottom: 20px;
  
  ${({ imageUrl }) => imageUrl && `
    background-image: url(${imageUrl});
    background-size: cover;
    background-position: center;
  `}
`;

const EventType = styled.p`
  font-size: 12px;
  color: #512A59;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px 0;
`;

const Title = styled.h1`
  color: #180018;
  font-size: 32px;
  margin: 0 0 20px 0;
`;

const Info = styled.p`
  color: #512A59;
  font-size: 14px;
  margin: 8px 0;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 20px;
`;

const PriceButton = styled.button`
  flex: 1;
  padding: 12px 32px;
  background: #FFFFFF;
  color: #512A59;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background: #DFB6B2;
  }
`;

const AddButton = styled.button`
  flex: 1;
  padding: 12px 32px;
  background: #854E6B;
  color: #FFFFFF;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #512A59;
  }
  
  &:disabled {
    background: #D9D9D9;
    cursor: not-allowed;
  }
`;

const FavoriteButton = styled.button`
  padding: 12px 20px;
  background: transparent;
  color: #854E6B;
  border: 2px solid #854E6B;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  
  &:hover {
    background: #854E6B;
    color: #FFFFFF;
  }
  
  ${({ isActive }) => isActive && `
    background: #854E6B;
    color: #FFFFFF;
  `}
`;

const InfoSection = styled.section`
  background: #FFFFFF;
  padding: 30px;
  border-radius: 16px;
  margin-bottom: 30px;
  color: #180018;
`;

const SectionTitle = styled.h2`
  background: #D9D9D9;
  color: #180018;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 18px;
  margin-bottom: 20px;
  display: inline-block;
`;

const InfoContent = styled.div`
  background: #D9D9D9;
  padding: 20px;
  border-radius: 8px;
  line-height: 1.8;
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

const EventDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isAdding, setIsAdding] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const userId = useMemo(() => {
    const auth = localStorage.getItem('auth');
    return auth ? JSON.parse(auth).userId : null;
  }, []);
  
  const { event, loading, error, refetch } = useEvent(id);

  const handleAddToSchedule = useCallback(async () => {
    if (!userId || !event?.id || isAdding) return;
    
    try {
      setIsAdding(true);
      await scheduleAPI.addPlatformEvent(userId, event.id);
      refetch();
    } catch (err) {
      console.error('Error adding to schedule:', err);
      alert('Не удалось добавить событие в расписание');
    } finally {
      setIsAdding(false);
    }
  }, [userId, event?.id, isAdding, refetch]);

  const handleToggleFavorite = useCallback(async () => {
    if (!userId || !event?.id) return;
    
    try {
      if (!isFavorite) {
        await scheduleAPI.addToFavorites(userId, event.id);
        setIsFavorite(true);
      } else {
        await scheduleAPI.removeFromFavorites(userId, event.id);
        setIsFavorite(false);
      }
    } catch (err) {
      console.error('Error toggling favorite:', err);
      alert('Не удалось обновить избранное');
    }
  }, [userId, event?.id, isFavorite]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Дата не указана';
    try {
      const date = new Date(dateString.includes('T') ? dateString : dateString.replace(' ', 'T'));
      if (isNaN(date.getTime())) return 'Дата не указана';
      return date.toLocaleString('ru-RU', {
        day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch {
      return 'Дата не указана';
    }
  };

  if (loading) {
    return (
      <PageContainer>
        <Loader>Загрузка события...</Loader>
      </PageContainer>
    );
  }

  if (error || !event) {
    return (
      <PageContainer>
        <ErrorMessage>
          Не удалось загрузить событие. <br />
          <button 
            onClick={() => navigate(-1)} 
            style={{ marginTop: '20px', padding: '10px 20px', background: '#854E6B', color: '#fff', border: 'none', borderRadius: '20px', cursor: 'pointer' }}
          >
            Назад
          </button>
        </ErrorMessage>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <EventHero>
        <ContentWrapper>
          <EventCard>
            <EventImage imageUrl={event.image} />
            <EventType>{event.type || 'Мероприятие'}</EventType>
            <Title>{event.name}</Title>
            <Info>📅 {formatDate(event.start || event.date_begin)}</Info>
            <Info>📍 {event.location}</Info>
            <ButtonGroup>
              <PriceButton>{event.price ? `${event.price} ₽` : 'Бесплатно'}</PriceButton>
              <AddButton onClick={handleAddToSchedule} disabled={isAdding || !userId}>
                {isAdding ? 'Добавление...' : !userId ? 'Войдите' : 'В календарь'}
              </AddButton>
              <FavoriteButton 
                onClick={handleToggleFavorite}
                isActive={isFavorite}
                disabled={!userId}
                aria-label={isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'}
              >
                {isFavorite ? '⭐' : '☆'}
              </FavoriteButton>
            </ButtonGroup>
          </EventCard>
        </ContentWrapper>
      </EventHero>

      <InfoSection>
        <ContentWrapper>
          <SectionTitle>О мероприятии</SectionTitle>
          <InfoContent>
            <p><strong>Время:</strong> {formatDate(event.start || event.date_begin)} - {formatDate(event.end || event.date_end)}</p>
            <p><strong>Место:</strong> {event.location}</p>
            {event.description && (
              <>
                <p style={{ marginTop: '20px' }}><strong>Описание:</strong></p>
                <p>{event.description}</p>
              </>
            )}
          </InfoContent>
          
          <div style={{ marginTop: '40px' }}>
            <SectionTitle>Рекомендации для вас</SectionTitle>
            <Recommendations />
          </div>
        </ContentWrapper>
      </InfoSection>
    </PageContainer>
  );
};

export default EventDetailPage;

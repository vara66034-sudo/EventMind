import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import TypeFilters from '../components/events/TypeFilters';
import Calendar from '../components/events/Calendar';
import Recommendations from '../components/events/Recommendations';

const PageContainer = styled.div`
  min-height: 100vh;
`;

// Фиолетовый блок с основной информацией
const EventHero = styled.section`
  background: #2B124C;
  padding: 40px 0;
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

// Карточка события
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

const PriceButton = styled.button`
  display: inline-block;
  padding: 12px 32px;
  background: #FFFFFF;
  color: #512A59;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 20px;
  
  &:hover {
    background: #DFB6B2;
  }
`;

// Белый блок с информацией
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

const EventDetailPage = () => {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [activeType, setActiveType] = useState('Все мероприятия');

  useEffect(() => {
    // Моковые данные (потом заменим на API)
    setEvent({
      id: parseInt(id),
      date_end: '2024-04-15 22:00:00',
      description: 'Это будет незабываемый вечер! Живая музыка, световое шоу и отличная атмосфера. Не пропустите!',
      name: 'EventMind AI Hackathon 2026',
      date_begin: '2026-05-20 10:00:00',
      location: 'Екатеринбург, Технопарк',
      image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800'
    });
  }, [id]);

  const handleTypeChange = (type) => {
    setActiveType(type);
  };

  if (!event) return <div>Загрузка...</div>;

  const formatDate = (dateString) => {
    if (!dateString) return 'Дата не указана';
    try {
      const date = new Date(dateString.replace(' ', 'T'));
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Дата не указана';
    }
  };

  return (
    <PageContainer>
      {/* Белая полоса с типами */}
      <TypeFilters activeType={activeType} onTypeChange={handleTypeChange} />

      {/* Фиолетовый блок с карточкой события */}
      <EventHero>
        <ContentWrapper>
          <EventCard>
            <EventImage imageUrl={event.image} />
            <EventType>Тип мероприятия</EventType>
            <Title>{event.name}</Title>
            <Info>📅 {formatDate(event.date_begin)}</Info>
            <Info>📍 {event.location}</Info>
            <PriceButton>Цена</PriceButton>
          </EventCard>
        </ContentWrapper>
      </EventHero>

      {/* Белый блок с информацией и рекомендациями */}
      <InfoSection>
        <ContentWrapper>
          <SectionTitle>О мероприятии</SectionTitle>
          <InfoContent>
            <p><strong>Время:</strong> {formatDate(event.date_begin)} - {formatDate(event.date_end)}</p>
            <p><strong>Место:</strong> {event.location}</p>
            <p style={{ marginTop: '20px' }}><strong>Описание:</strong></p>
            <p>{event.description}</p>
          </InfoContent>
          
          {/* Рекомендации (без календаря!) */}
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

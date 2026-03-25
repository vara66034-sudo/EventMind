import React, { useState } from 'react';
import styled from 'styled-components';
import EventCard from '../components/events/EventCard';
import Calendar from '../components/events/Calendar';
import Recommendations from '../components/events/Recommendations';
import TypeFilters from '../components/events/TypeFilters';
import useEvents from '../hooks/useEvents';

// Основной контейнер страницы
const PageContainer = styled.div`
  min-height: 100vh;
`;

// Блок событий (фиолетовый фон)
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
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #854E6B;
    border-radius: 4px;
  }
  
  @media (max-width: 768px) {
    gap: 15px;
  }
`;

// Блок календаря и рекомендаций (белый фон)
const InfoSection = styled.section`
  background: #FFFFFF;
  padding: 40px 0;
  color: #180018;
`;

// Loader
const Loader = styled.div`
  text-align: center;
  padding: 60px;
  color: #FFFFFF;
  font-size: 20px;
`;

// Сообщение об ошибке
const ErrorMessage = styled.div`
  text-align: center;
  padding: 60px;
  color: #DFB6B2;
  font-size: 18px;
`;

const EventsPage = () => {
  const [activeType, setActiveType] = useState('Все мероприятия');
  const [selectedCity, setSelectedCity] = useState(null);
  
  // Используем хук для загрузки событий с API
  const { events, loading, error } = useEvents({
    city: selectedCity,
    type: activeType !== 'Все мероприятия' ? activeType : null,
  });

  const handleTypeChange = (type) => {
    setActiveType(type);
  };

  const handleCitySelect = (city) => {
    setSelectedCity(city === 'Все города' ? null : city);
  };

  // Состояние загрузки
  if (loading) {
    return (
      <PageContainer>
        <TypeFilters activeType={activeType} onTypeChange={handleTypeChange} />
        <EventsSection>
          <ContentWrapper>
            <Loader>Загрузка событий...</Loader>
          </ContentWrapper>
        </EventsSection>
      </PageContainer>
    );
  }

  // Состояние ошибки
  if (error) {
    console.warn('API не доступен, используем тестовые данные:', error);
  }

  // Тестовые данные (если API не доступен)
  const mockEvents = [
    {
      id: 1,
      name: 'Концерт любимой группы',
      date_begin: '2024-04-15 19:00:00',
      location: 'Москва, Крокус Сити Холл',
      image: null,
    },
    {
      id: 2,
      name: 'Мастер-класс по фотографии',
      date_begin: '2024-04-20 14:00:00',
      location: 'Санкт-Петербург, Лофт Проект Этажи',
      image: null,
    },
    {
      id: 3,
      name: 'IT Конференция 2024',
      date_begin: '2024-05-01 10:00:00',
      location: 'Онлайн',
      image: null,
    },
    {
      id: 4,
      name: 'Джазовый вечер',
      date_begin: '2024-04-18 20:00:00',
      location: 'Екатеринбург',
      image: null,
    },
  ];

  // Используем данные из API или тестовые
  const displayEvents = events.length > 0 ? events : mockEvents;

  return (
    <PageContainer>
      {/* Белая полоса с типами мероприятий */}
      <TypeFilters activeType={activeType} onTypeChange={handleTypeChange} />

      {/* Основной блок с событиями (фиолетовый фон) */}
      <EventsSection>
        <ContentWrapper>
          <EventsGrid>
            {displayEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </EventsGrid>
        </ContentWrapper>
      </EventsSection>

      {/* Блок календаря и рекомендаций (белый фон) */}
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
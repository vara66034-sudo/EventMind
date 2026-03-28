import React, { useMemo, useState } from 'react';
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

  const data = useMemo(() => ({
        city: selectedCity,
    type: activeType !== 'Все мероприятия' ? activeType : null,
  }),[selectedCity, activeType])
  
  // Используем хук для загрузки событий с API
  const { events, loading, error } = useEvents(data);

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
      name: 'EventMind AI Hackathon 2026',
      date_begin: '2026-05-20 10:00:00',
      location: 'Екатеринбург, Технопарк',
      image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800'
    },
    {
      id: 4,
      name: 'Python & Data Science Meetup',
      date_begin: '2026-06-05 19:00:00',
      location: 'Екатеринбург, Ельцин Центр',
      image: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800'
    },
    {
      id: 5,
      name: 'Ural CyberSecurity Forum',
      date_begin: '2026-07-10 09:00:00',
      location: 'Екатеринбург-ЭКСПО',
      image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800'
    }, 
    {
      id: 6,
      name: 'EventMind AI Hackathon 2026',
      date_begin: '2026-04-15 19:00:00',
      location: 'Екатеринбург, Технопарк "Университетский"',
      image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800',
    },
    {
      id: 2,
      name: 'Python & Data Science Meetup',
      date_begin: '2026-04-20 14:00:00',
      location: 'Екатеринбург, Ельцин Центр',
      image: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800',
    },
    {
      id: 7,
      name: 'Ural CyberSecurity Forum 2026',
      date_begin: '2026-05-01 10:00:00',
      location: 'Екатеринбург-ЭКСПО',
      image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800',
    },
    {
      id: 8,
      name: 'Frontend Intensive: React & Next.js',
      date_begin: '2026-04-18 20:00:00',
      location: 'Онлайн (Zoom )',
      image: 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=800',
    },
    {
      id: 9,
      name: 'DevOps & Cloud Infrastructure Day',
      date_begin: '2026-05-12 11:00:00',
      location: 'Екатеринбург, БЦ "Высоцкий"',
      image: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
    },
    {
      id: 10,
      name: 'GameDev Weekend: Unity & Unreal',
      date_begin: '2026-05-25 12:00:00',
      location: 'Екатеринбург, Коворкинг "Names"',
      image: 'https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=800',
    },
    {
      id: 11,
      name: 'Mobile Conf: iOS & Android Trends',
      date_begin: '2026-06-05 10:00:00',
      location: 'Екатеринбург, Хаятт Ридженси',
      image: 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800',
    },
    {
      id: 12,
      name: 'Product Management Workshop',
      date_begin: '2026-06-15 18:30:00',
      location: 'Онлайн',
      image: 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=800',
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

import React from 'react';
import styled from 'styled-components';
import RecommendationCard from './RecommendationCard';

const Container = styled.section`
  margin: 40px 0;
  padding: 0 40px;
  
  @media (max-width: 768px) {
    padding: 0 20px;
  }
`;

const Title = styled.h2`
  color: #180018;
  margin-bottom: 25px;
  font-size: 24px;
  font-weight: 700;
`;

const Grid = styled.div`
  display: flex;
  gap: 20px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding-bottom: 20px;
  
  &::-webkit-scrollbar {
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #854E6B;
    border-radius: 4px;
  }
`;

// Тестовые данные для рекомендаций
const recommendedEvents = [
  {
    id: 101,
    name: 'Джазовый вечер',
    date_begin: '2024-04-18 20:00:00',
    location: 'Москва',
    image: null,
  },
  {
    id: 102,
    name: 'Стендап шоу',
    date_begin: '2024-04-22 19:00:00',
    location: 'Санкт-Петербург',
    image: null,
  },
  {
    id: 103,
    name: 'Арт-выставка',
    date_begin: '2024-04-25 11:00:00',
    location: 'Екатеринбург',
    image: null,
  },
  {
    id: 104,
    name: 'Кулинарный мастер-класс',
    date_begin: '2024-04-28 15:00:00',
    location: 'Казань',
    image: null,
  },
];

const Recommendations = () => {
  return (
    <Container>
      <Title>Рекомендации для вас</Title>
      <Grid>
        {recommendedEvents.map((event) => (
          <RecommendationCard key={event.id} event={event} />
        ))}
      </Grid>
    </Container>
  );
};

export default Recommendations;

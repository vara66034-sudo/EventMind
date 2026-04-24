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
    id: 67,
    name: 'ИТ-Конференция',
    date_begin: '2024-04-18 20:00:00',
    location: 'Москва',
    image: "https://it-elements.ru/images/tild6333-3332-4531-a238-643733316137__rectangle_167_1.jpg",
  },
  {
    id: 2,
    name: 'ЕКОД',
    date_begin: '2024-04-22 19:00:00',
    location: 'Санкт-Петербург',
    image: "https://www.sostav.ru/images/news/2024/10/28/8hmzdk0w.jpg",
  },
  {
    id: 66,
    name: 'Dev.by',
    date_begin: '2024-04-25 11:00:00',
    location: 'Екатеринбург',
    image: "https://avatars.mds.yandex.net/i?id=915530a742b985ef93a5b7561b5c5803_l-4353628-images-thumbs&n=13",
  },
  {
    id: 12,
    name: 'ГеймДев',
    date_begin: '2024-04-28 15:00:00',
    location: 'Казань',
    image: "https://cdn.tvspb.ru/storage/wp-content/uploads/2025/11/montazh.00_05_41_05.still381.jpg__0_0x0.jpg",
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

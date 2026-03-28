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
    image: "https://avatars.mds.yandex.net/get-afishanew/5098259/a95faf50c562e9510cbef1b5b0129dd2/960x690_noncrop",
  },
  {
    id: 102,
    name: 'Стендап шоу',
    date_begin: '2024-04-22 19:00:00',
    location: 'Санкт-Петербург',
    image: "https://avatars.mds.yandex.net/get-tv-shows/27487/2a00000197ac73efa20894ade83f2626fd18/640x640",
  },
  {
    id: 103,
    name: 'Арт-выставка',
    date_begin: '2024-04-25 11:00:00',
    location: 'Екатеринбург',
    image: "https://avatars.mds.yandex.net/i?id=7d13bebc6a28f52ffbf9b403dcec97c7_l-5906493-images-thumbs&n=13",
  },
  {
    id: 104,
    name: 'Кулинарный мастер-класс',
    date_begin: '2024-04-28 15:00:00',
    location: 'Казань',
    image: "https://pro-interactive.ru/netcat_files/generated/44/160/400x400/43339/210104/7cbcf5a1a645993425c173118d0bced5.jpg?crop=0%3A0%3A0%3A0&hash=5be2b729d20d97f6cc0fe0861b6a7318&resize_mode=1&wm_m=0",
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

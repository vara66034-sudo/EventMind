import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const Card = styled(Link)`
  flex: 0 0 380px;
  scroll-snap-align: start;
  display: block;
  background: #FBE4D8;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  padding: 25px;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(133, 78, 107, 0.3);
  }
  
  @media (max-width: 768px) {
    flex: 0 0 300px;
    padding: 20px;
  }
`;

const CardImage = styled.div`
  width: 100%;
  height: 180px;
  background: #FBE4D8;  /* бежевый фон вместо градиента */
  border-radius: 16px;
  margin-bottom: 16px;
  
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

const Title = styled.h3`
  margin: 0 0 12px 0;
  color: #180018;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.3;
`;

const Info = styled.p`
  color: #512A59;
  font-size: 14px;
  margin: 6px 0;
  line-height: 1.5;
`;

const PriceButton = styled.div`
  display: inline-block;
  padding: 10px 24px;
  background: #FFFFFF;
  color: #512A59;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-top: 12px;
  text-align: center;
`;

const EventCard = ({ event }) => {
  const formatDate = (dateString) => {
    if (!dateString || typeof dateString !== 'string') {
      return 'Дата не указана';
    }
    
    try {
      const dateStringFormatted = dateString.replace(' ', 'T');
      const date = new Date(dateStringFormatted);
      
      if (isNaN(date.getTime())) {
        return 'Дата не указана';
      }
      
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Дата не указана';
    }
  };

  return (
    <Card to={`/events/${event.id}`}>
      <div>
        <CardImage imageUrl={event.image} />
        <EventType>Тип мероприятия</EventType>
        <Title>{event.name}</Title>
        <Info>{formatDate(event.date_begin)}</Info>
        {event.location && <Info>{event.location}</Info>}
      </div>
      <PriceButton>Цена</PriceButton>
    </Card>
  );
};

export default EventCard;
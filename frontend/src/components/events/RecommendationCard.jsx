import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const Card = styled(Link)`
  flex: 0 0 320px;
  scroll-snap-align: start;
  display: block;
  background: #512A59;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(133, 78, 107, 0.4);
  }
  
  @media (max-width: 768px) {
    flex: 0 0 280px;
  }
`;

const CardImage = styled.div`
  width: 100%;
  height: 380px;
  background: linear-gradient(135deg, #854E6B 0%, #512A59 100%);
  
  ${({ imageUrl }) => imageUrl && `
    background-image: url(${imageUrl});
    background-size: cover;
    background-position: center;
  `}
`;

const RecommendationCard = ({ event }) => {
  return (
    <Card to={`/events/${event.id}`}>
      <CardImage imageUrl={event.image} />
    </Card>
  );
};

export default RecommendationCard;

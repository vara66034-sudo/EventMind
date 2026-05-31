import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const Card = styled(Link)`
  display: block;
  flex: 0 0 300px;
  background: #512A59;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  aspect-ratio: 1 / 1;
  scroll-snap-align: start;
  position: relative;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(133, 78, 107, 0.4);
  }
`;

const CardImage = styled.div`
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #854E6B 0%, #512A59 100%);
  
  ${({ imageUrl }) => imageUrl && `
    background-image: url(${imageUrl});
    background-size: cover;
    background-position: center;
  `}
`;

const TitleOverlay = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 15px;
  background: rgba(81, 42, 89, 0.85);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
  backdrop-filter: blur(4px);
`;

const RecommendationCard = ({ event }) => {
  return (
    <Card to={`/events/${event.id}`}>
      <CardImage imageUrl={event.image} />
      <TitleOverlay>{event.name || event.title}</TitleOverlay>
    </Card>
  );
};

export default RecommendationCard;

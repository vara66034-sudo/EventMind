import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const Card = styled.article`
  flex: 0 0 380px;
  min-width: 380px;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  background: #FBE4D8;
  border-radius: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  color: inherit;
  padding: 25px;
  min-height: 320px;
  height: auto;
  overflow: visible;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(133, 78, 107, 0.3);
  }

  @media (max-width: 1024px) {
    flex: 0 0 320px;
    min-width: 320px;
    padding: 20px;
  }

  @media (max-width: 480px) {
    flex: 0 0 85vw;
    min-width: 85vw;
    padding: 20px;
    min-height: 300px;
  }
`;

const ClickableArea = styled.div`
  cursor: pointer;
`;

const CardImage = styled.div`
  width: 100%;
  height: 180px;
  flex-shrink: 0;
  background: #FBE4D8;
  border-radius: 16px;
  margin-bottom: 16px;

  ${({ imageUrl }) =>
    imageUrl &&
    `
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
  line-height: 1.35;

  white-space: normal;
  overflow: visible;
  text-overflow: unset;
  display: block;
  overflow-wrap: anywhere;
  word-break: normal;
`;

const Info = styled.p`
  color: #512A59;
  font-size: 14px;
  margin: 6px 0;
  line-height: 1.5;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 16px;
  flex-wrap: wrap;
`;

const PriceButton = styled.div`
  flex: 1 1 120px;
  padding: 10px 12px;
  background: #FFFFFF;
  color: #512A59;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
`;

const AddButton = styled.button`
  flex: 1 1 120px;
  padding: 10px 12px;
  background: #854E6B;
  color: #FFFFFF;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: #512A59;
  }
`;

const FavoriteButton = styled.button`
  width: 48px;
  padding: 10px 12px;
  background: transparent;
  color: #854E6B;
  border: 2px solid #854E6B;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #854E6B;
    color: #FFFFFF;
  }

  ${({ $isActive }) =>
    $isActive &&
    `
      background: #854E6B;
      color: #FFFFFF;
    `}
`;

const EventCard = ({
  event,
  userId,
  onAddToSchedule,
  onToggleFavorite,
  isFavorite = false,
}) => {
  const navigate = useNavigate();

  const eventId = Number(event?.id ?? event?.event_id);

  const formatDate = (dateString) => {
    if (!dateString) return 'Дата не указана';

    try {
      const cleanValue = String(dateString).replace(' ', 'T').replace(/Z$/, '');
      const date = new Date(cleanValue);

      if (Number.isNaN(date.getTime())) return 'Дата не указана';

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

  const handleOpenEvent = useCallback(() => {
    if (Number.isFinite(eventId)) {
      navigate(`/events/${eventId}`);
    }
  }, [navigate, eventId]);

  const handleAddClick = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();

      if (!userId) {
        alert('Войдите в аккаунт, чтобы добавить событие в календарь');
        return;
      }

      if (onAddToSchedule && Number.isFinite(eventId)) {
        onAddToSchedule(userId, eventId);
      }
    },
    [onAddToSchedule, userId, eventId]
  );

  const handleFavoriteClick = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();

      if (!userId) {
        alert('Войдите в аккаунт, чтобы добавить событие в избранное');
        return;
      }

      if (onToggleFavorite && Number.isFinite(eventId)) {
        onToggleFavorite(userId, eventId, !isFavorite);
      }
    },
    [onToggleFavorite, userId, eventId, isFavorite]
  );

  return (
    <Card>
      <ClickableArea onClick={handleOpenEvent}>
        <CardImage imageUrl={event.image || event.image_url} />

        <EventType>{event.type || 'Мероприятие'}</EventType>

        <Title>{event.name || event.title || 'Без названия'}</Title>

        <Info>{formatDate(event.start || event.date_begin || event.event_date)}</Info>

        {event.location && <Info>{event.location}</Info>}
      </ClickableArea>

      <ButtonGroup>
        <PriceButton>
          {event.price ? `${event.price} ₽` : 'Бесплатно'}
        </PriceButton>

        <AddButton type="button" onClick={handleAddClick}>
          В календарь
        </AddButton>

        <FavoriteButton
          type="button"
          onClick={handleFavoriteClick}
          $isActive={isFavorite}
          aria-label={isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
        >
          {isFavorite ? '⭐' : '☆'}
        </FavoriteButton>
      </ButtonGroup>
    </Card>
  );
};

export default EventCard;

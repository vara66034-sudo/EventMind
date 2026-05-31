import React, { useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import RecommendationCard from './RecommendationCard';
import { userAPI } from '../../services/api';

const Container = styled.section`
  margin: 40px 0;
  padding: 0;
`;

const Title = styled.h2`
  color: #180018;
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: 700;
`;

const AdviceContainer = styled.div`
  background: #FBE4D8;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
  color: #512A59;
  font-size: 15px;
  line-height: 1.6;
  border-left: 4px solid #854E6B;
  white-space: pre-wrap;
`;

const Grid = styled.div`
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  gap: 20px;
  padding-bottom: 20px;
  scroll-snap-type: x mandatory;
  
  &::-webkit-scrollbar {
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(81, 42, 89, 0.1);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #854E6B;
    border-radius: 4px;
  }
`;

const Loader = styled.div`
  padding: 20px;
  color: #512A59;
  text-align: center;
`;

const Recommendations = () => {
  const [events, setEvents] = useState([]);
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(true);

  const userId = useMemo(() => {
    const auth = localStorage.getItem('auth');
    return auth ? JSON.parse(auth).userId : null;
  }, []);

  useEffect(() => {
    if (!userId) {
      setLoading(false);
      return;
    }
    
    const fetchRecs = async () => {
      try {
        setLoading(true);
        const res = await userAPI.getRecommendationsWithSchedule(userId, 10);
        if (res && res.success) {
          const mapped = Array.isArray(res.data) ? res.data.map(item => item.event || item) : [];
          setEvents(mapped);
          setAdvice(res.ai_advice || '');
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecs();
  }, [userId]);

  if (loading) {
    return <Loader>Загрузка рекомендаций...</Loader>;
  }

  if (!events.length) {
    return null;
  }

  return (
    <Container>
      <Title>Рекомендации</Title>
      {advice && <AdviceContainer>{advice}</AdviceContainer>}
      <Grid>
        {events.map((event) => (
          <RecommendationCard key={event.id} event={event} />
        ))}
      </Grid>
    </Container>
  );
};

export default Recommendations;

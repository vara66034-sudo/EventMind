import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';

const Container = styled.div`
  text-align: center;
  padding: 100px 20px;
  background: linear-gradient(135deg, #2B124C 0%, #512A59 100%);
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const Title = styled.h1`
  color: #FFFFFF;
  font-size: 48px;
  margin-bottom: 20px;
  
  @media (max-width: 768px) {
    font-size: 32px;
  }
`;

const Subtitle = styled.p`
  color: #D9D9D9;
  font-size: 20px;
  margin-bottom: 50px;
  max-width: 600px;
  line-height: 1.6;
  
  @media (max-width: 768px) {
    font-size: 16px;
    margin-bottom: 40px;
  }
`;

const ButtonsWrapper = styled.div`
  display: flex;
  gap: 25px;
  flex-wrap: wrap;
  justify-content: center;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }
`;

// Создаём стилизованную ссылку-кнопку
const StyledLink = styled(Link)`
  display: inline-block;
  padding: 15px 40px;
  background: linear-gradient(135deg, #854E6B 0%, #512A59 100%);
  color: #FFFFFF;
  text-decoration: none;
  border-radius: 25px;
  font-size: 20px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(133, 78, 107, 0.4);
  }
  
  &:active {
    transform: translateY(-1px);
  }
`;

const StyledLinkWhite = styled(StyledLink)`
  background: #FFFFFF;
  color: #512A59;
  
  &:hover {
    background: #DFB6B2;
  }
`;

const HomePage = () => {
  return (
    <Container>
      <Title>Добро пожаловать в EventMind</Title>
      <Subtitle>
        Находи лучшие события в твоём городе и создавай свои собственные
      </Subtitle>
      <ButtonsWrapper>
        <StyledLink to="/events">
          Смотреть события
        </StyledLink>
        <StyledLinkWhite to="/login">
          Создать событие
        </StyledLinkWhite>
      </ButtonsWrapper>
    </Container>
  );
};

export default HomePage;

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import SearchBar from '../common/SearchBar';
import AiResponseModal from '../common/AiResponseModal';
import { eventsAPI } from '../../services/api';

const HeaderContainer = styled.header`
  background: #190019;
  padding: 15px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Nav = styled.nav`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  
  @media (max-width: 768px) {
    flex-wrap: wrap;
    padding: 0 20px;
    gap: 15px;
  }
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

// 🔥 Статичная кнопка города (вместо CitySelector)
const CityButton = styled.div`
  background: #FBE4D8;
  color: #512A59;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  cursor: default;
`;

const ProfileLink = styled(Link)`
  color: #FFFFFF;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    color: #DFB6B2;
  }
`;

const Divider = styled.span`
  color: #512A59;
`;

const Header = () => {
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiAnswer, setAiAnswer] = useState('');
  const [isAiLoading, setIsAiLoading] = useState(false);

  const handleSearch = async (query) => {
    setAiQuestion(query);
    setIsAiModalOpen(true);
    setIsAiLoading(true);
    setAiAnswer('');

    try {
      const response = await eventsAPI.askAi(query);
      if (response && response.success) {
        setAiAnswer(response.data.answer);
      } else {
        setAiAnswer(response?.error || 'Извините, возникла ошибка при получении ответа от ИИ.');
      }
    } catch (error) {
      console.error('Error asking AI:', error);
      setAiAnswer('Не удалось связаться с ИИ. Проверьте подключение к серверу.');
    } finally {
      setIsAiLoading(false);
    }
  };

  return (
    <HeaderContainer>
      <Nav>
        <LeftSection>
          <CityButton>Екатеринбург</CityButton>
          <SearchBar onSearch={handleSearch} />
        </LeftSection>
        <RightSection>
          <ProfileLink to="/">События</ProfileLink>
          <Divider>/</Divider>
          <ProfileLink to="/profile">Мой профиль</ProfileLink>
          <Divider>/</Divider>
          <ProfileLink to="/login">Войти</ProfileLink>
        </RightSection>
      </Nav>

      <AiResponseModal 
        isOpen={isAiModalOpen} 
        onClose={() => setIsAiModalOpen(false)}
        question={aiQuestion}
        answer={aiAnswer}
        isLoading={isAiLoading}
      />
    </HeaderContainer>
  );
};

export default Header;

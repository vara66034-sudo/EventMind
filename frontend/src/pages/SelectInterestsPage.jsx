import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AVAILABLE_TAGS } from '../constants/tags';
import { authAPI, userAPI } from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #2B124C 0%, #512A59 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
`;

const ContentWrapper = styled.div`
  max-width: 800px;
  width: 100%;
  background: #FFFFFF;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  text-align: center;
`;

const Title = styled.h1`
  color: #180018;
  margin-bottom: 10px;
  font-size: 28px;
`;

const Subtitle = styled.p`
  color: #512A59;
  margin-bottom: 30px;
  font-size: 16px;
  line-height: 1.5;
`;

const TagsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 40px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  
  /* Скроллбар для списка тегов */
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #D9D9D9;
    border-radius: 3px;
  }
`;

const TagButton = styled.button`
  padding: 12px 16px;
  border: 2px solid ${({ isSelected }) => (isSelected ? '#854E6B' : '#D9D9D9')};
  border-radius: 12px;
  background: ${({ isSelected }) => (isSelected ? '#854E6B' : '#FFFFFF')};
  color: ${({ isSelected }) => (isSelected ? '#FFFFFF' : '#512A59')};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #854E6B;
    transform: translateY(-2px);
  }
  
  ${({ isSelected }) => isSelected && `
    box-shadow: 0 4px 10px rgba(133, 78, 107, 0.3);
  `}
`;

const Actions = styled.div`
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
`;

const Button = styled.button`
  padding: 14px 32px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  
  ${({ secondary }) =>
    secondary
      ? `
      background: transparent;
      color: #512A59;
      border: 2px solid #D9D9D9;
      
      &:hover {
        border-color: #854E6B;
        color: #854E6B;
      }
    `
      : `
      background: #854E6B;
      color: #FFFFFF;
      
      &:hover {
        background: #512A59;
      }
      
      &:disabled {
        background: #D9D9D9;
        cursor: not-allowed;
      }
  `}
`;

const SelectInterestsPage = () => {
  const navigate = useNavigate();
  const [selectedTags, setSelectedTags] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const userId = useMemo(() => {
    const auth = localStorage.getItem('auth');
    return auth ? JSON.parse(auth).userId : null;
  }, []);

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleContinue = async () => {
    if (selectedTags.length === 0) return;
    
    setIsSubmitting(true);
    
    try {
      const pendingRegistration = localStorage.getItem('pendingRegistration');
      
      if (pendingRegistration) {
        const userData = JSON.parse(pendingRegistration);

        const response = await authAPI.register({
          name: userData.name,
          email: userData.email,
          password: userData.password,
          interests: selectedTags,
        });
        
        console.log('Registration response:', response);
        if (response && response.success && response.data) {
          console.log('Setting auth with userId:', response.data.user_id);
          localStorage.setItem('auth', JSON.stringify({
            userId: response.data.user_id,
            token: response.data.token,
            user: response.data,
          }));
        }
        
        localStorage.removeItem('pendingRegistration');
        
      } else if (userId) {
        await userAPI.updateProfile(userId, {
          interests: selectedTags,
        });
      }
      
      navigate('/profile');
      
    } catch (error) {
      console.error('Error saving interests:', error);
      alert('Не удалось сохранить интересы. Попробуйте ещё раз.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = async () => {
    const pendingRegistration = localStorage.getItem('pendingRegistration');
    
    if (pendingRegistration) {
      try {
        const userData = JSON.parse(pendingRegistration);
        const response = await authAPI.register({
          name: userData.name,
          email: userData.email,
          password: userData.password,
          interests: [],
        });
        
        if (response && response.success && response.data) {
          localStorage.setItem('auth', JSON.stringify({
            userId: response.data.user_id,
            token: response.data.token,
            user: response.data,
          }));
        }
        
        localStorage.removeItem('pendingRegistration');
      } catch (error) {
        console.error('Error registering without interests:', error);
      }
    }
    
    navigate('/profile');
  };

  return (
    <PageContainer>
      <ContentWrapper>
        <Title>Что вам интересно?</Title>
        <Subtitle>
          Выберите несколько тем, чтобы мы могли подбирать для вас лучшие мероприятия
        </Subtitle>

        <TagsGrid>
          {AVAILABLE_TAGS.map((tag) => (
            <TagButton
              key={tag}
              isSelected={selectedTags.includes(tag)}
              onClick={() => toggleTag(tag)}
              disabled={isSubmitting}
            >
              {tag}
            </TagButton>
          ))}
        </TagsGrid>

        <Actions>
          <Button 
            secondary 
            onClick={handleSkip}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Загрузка...' : 'Пропустить'}
          </Button>
          <Button 
            onClick={handleContinue} 
            disabled={selectedTags.length === 0 || isSubmitting}
          >
            {isSubmitting ? 'Сохранение...' : `Продолжить (${selectedTags.length})`}
          </Button>
        </Actions>
      </ContentWrapper>
    </PageContainer>
  );
};

export default SelectInterestsPage;

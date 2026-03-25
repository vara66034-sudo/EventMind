import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { userAPI } from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
  background: #190019;
  padding: 40px 0;
`;

const ContentWrapper = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 0 40px;
`;

const FormContainer = styled.div`
  background: #FFFFFF;
  border-radius: 24px;
  padding: 40px;
  color: #180018;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 30px;
  color: #180018;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: #512A59;
`;

const Input = styled.input`
  padding: 15px 20px;
  border: 2px solid #D9D9D9;
  border-radius: 12px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #854E6B;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  margin-top: 20px;
`;

const Button = styled.button`
  flex: 1;
  padding: 15px 30px;
  background: ${({ secondary }) => secondary ? '#D9D9D9' : '#854E6B'};
  color: ${({ secondary }) => secondary ? '#180018' : '#FFFFFF'};
  border: none;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background: ${({ secondary }) => secondary ? '#DFB6B2' : '#512A59'};
  }
`;

const EditProfilePage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState({
    name: '',
    email: '',
    phone: '',
    avatar: null,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      // const userData = await userAPI.getProfile();
      // setUser(userData);
      
      // Тестовые данные
      setUser({
        name: 'Имя Фамилия',
        email: 'user@example.com',
        phone: '+7 (999) 999-99-99',
      });
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // await userAPI.updateProfile(user);
      alert('Профиль обновлён!');
      navigate('/profile');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Ошибка обновления профиля');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  return (
    <PageContainer>
      <ContentWrapper>
        <FormContainer>
          <Title>Редактировать профиль</Title>
          
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label>Имя</Label>
              <Input
                type="text"
                name="name"
                value={user.name}
                onChange={handleChange}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Email</Label>
              <Input
                type="email"
                name="email"
                value={user.email}
                onChange={handleChange}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Телефон</Label>
              <Input
                type="tel"
                name="phone"
                value={user.phone}
                onChange={handleChange}
              />
            </FormGroup>

            <ButtonGroup>
              <Button type="button" secondary onClick={() => navigate('/profile')}>
                Отмена
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Сохранение...' : 'Сохранить'}
              </Button>
            </ButtonGroup>
          </Form>
        </FormContainer>
      </ContentWrapper>
    </PageContainer>
  );
};

export default EditProfilePage;
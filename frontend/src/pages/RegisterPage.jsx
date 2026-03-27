import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import TypeFilters from '../components/events/TypeFilters';

const PageContainer = styled.div`
  min-height: 100vh;
  background: #2B124C;
`;

const ContentWrapper = styled.div`
  max-width: 500px;
  margin: 0 auto;
  padding: 80px 20px;
`;

const FormContainer = styled.div`
  background: #FFFFFF;
  border-radius: 24px;
  padding: 40px;
  color: #180018;
`;

const Title = styled.h1`
  color: #180018;
  text-align: center;
  margin-bottom: 30px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
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

const Button = styled.button`
  padding: 15px 30px;
  background: #854E6B;
  color: #FFFFFF;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background: #512A59;
  }
`;

const LinkText = styled.p`
  text-align: center;
  margin-top: 20px;
  
  a {
    color: #854E6B;
    text-decoration: none;
    font-weight: 600;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const RegisterPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // TODO: Интеграция с API
      // const response = await api.post('/api/auth/register', { name, email, password });
      
      alert('Регистрация будет реализована после интеграции с API');
      navigate('/login');
    } catch (error) {
      console.error('Register error:', error);
      alert('Ошибка регистрации');
    }
  };

  return (
    <PageContainer>
      <TypeFilters activeType="" onTypeChange={() => {}} />
      <ContentWrapper>
        <FormContainer>
          <Title>Регистрация</Title>
          <Form onSubmit={handleSubmit}>
            <Input
              type="text"
              placeholder="Имя"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button type="submit">Зарегистрироваться</Button>
          </Form>
          <LinkText>
            Уже есть аккаунт? <Link to="/login">Войти</Link>
          </LinkText>
        </FormContainer>
      </ContentWrapper>
    </PageContainer>
  );
};

export default RegisterPage;

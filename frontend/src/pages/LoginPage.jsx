import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { authAPI } from '../services/api';

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
  
  &:disabled {
    background: #D9D9D9;
    cursor: not-allowed;
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

const ErrorMessage = styled.p`
  color: #DFB6B2;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
`;

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    
    try {
      const response = await authAPI.login(email, password);
      
      if (response && response.success && response.data) {
        localStorage.setItem('auth', JSON.stringify({
          userId: response.data.user_id,
          token: response.data.token,
          user: response.data,
        }));
        navigate('/profile');
      } else {
        setError(response.error || 'Неверный ответ сервера');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Не удалось войти. Проверьте данные или подключение к серверу.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageContainer>
      <ContentWrapper>
        <FormContainer>
          <Title>Вход</Title>
          <Form onSubmit={handleSubmit}>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isSubmitting}
            />
            <Input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isSubmitting}
            />
            {error && <ErrorMessage>{error}</ErrorMessage>}
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Вход...' : 'Войти'}
            </Button>
          </Form>
          <LinkText>
            Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
          </LinkText>
        </FormContainer>
      </ContentWrapper>
    </PageContainer>
  );
};

export default LoginPage;

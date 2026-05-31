import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { authAPI } from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #2B124C 0%, #512A59 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
`;

const ContentWrapper = styled.div`
  max-width: 400px;
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
  font-size: 24px;
`;

const Subtitle = styled.p`
  color: #512A59;
  margin-bottom: 30px;
  font-size: 14px;
  line-height: 1.5;
`;

const EmailHint = styled.p`
  color: #854E6B;
  font-size: 14px;
  margin-bottom: 25px;
  font-weight: 500;
`;

const CodeInputContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
`;

const CodeInput = styled.input`
  width: 50px;
  height: 60px;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  border: 2px solid #D9D9D9;
  border-radius: 12px;
  background: #FBE4D8;
  color: #180018;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #854E6B;
    background: #FFFFFF;
  }
  
  &::placeholder {
    color: #D9D9D9;
  }
`;

const ResendButton = styled.button`
  background: transparent;
  color: #854E6B;
  border: none;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.2s ease;
  margin-bottom: 20px;
  
  &:hover {
    background: rgba(133, 78, 107, 0.1);
  }
  
  &:disabled {
    color: #D9D9D9;
    cursor: not-allowed;
  }
`;

const VerifyButton = styled.button`
  width: 100%;
  padding: 14px 32px;
  background: #854E6B;
  color: #FFFFFF;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #512A59;
  }
  
  &:disabled {
    background: #D9D9D9;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.p`
  color: #DFB6B2;
  font-size: 14px;
  margin-top: 15px;
  min-height: 20px;
`;

const TimerText = styled.span`
  color: #D9D9D9;
  font-size: 12px;
  margin-left: 8px;
`;

const VerifyEmailPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);
  const inputRefs = useRef([]);

  const email = location.state?.email || '';

  useEffect(() => {
    if (!email) {
      navigate('/register');
      return;
    }

    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendTimer, email, navigate]);

  const handleChange = (index, value) => {
    if (!/^\d?$/.test(value)) return;
    
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    setError('');

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pasted) {
      const newCode = [...code];
      for (let i = 0; i < Math.min(pasted.length, 6); i++) {
        newCode[i] = pasted[i];
      }
      setCode(newCode);
      const nextIndex = Math.min(pasted.length, 5);
      inputRefs.current[nextIndex]?.focus();
    }
  };

  const handleVerify = async () => {
    const verificationCode = code.join('');
    if (verificationCode.length !== 6) {
      setError('Введите все 6 цифр кода');
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      const response = await authAPI.verifyEmail({ email, code: verificationCode });
      if (response && response.success) {
        navigate('/select-interests', { state: { email } });
      } else {
        setError(response.error || 'Неверный код. Попробуйте ещё раз.');
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError('Произошла ошибка при проверке кода.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    if (resendTimer > 0) return;
    
    try {
      const response = await authAPI.resendVerificationCode({ email });
      if (response && response.success) {
        setResendTimer(60);
        setError('');
      } else {
        setError(response.error || 'Не удалось отправить код повторно');
      }
    } catch (err) {
      console.error('Resend error:', err);
      setError('Произошла ошибка при отправке кода.');
    }
  };

  const isCodeComplete = code.every((digit) => digit !== '');

  return (
    <PageContainer>
      <ContentWrapper>
        <Title>Подтверждение email</Title>
        <Subtitle>
          Мы отправили 6-значный код на вашу почту. Введите его ниже, чтобы завершить регистрацию.
        </Subtitle>
        
        {email && <EmailHint>{email}</EmailHint>}
        
        <CodeInputContainer onPaste={handlePaste}>
          {code.map((digit, index) => (
            <CodeInput
              key={index}
              ref={(el) => (inputRefs.current[index] = el)}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              disabled={isVerifying}
            />
          ))}
        </CodeInputContainer>

        <ResendButton 
          onClick={handleResend} 
          disabled={resendTimer > 0 || isVerifying}
        >
          Отправить код повторно
          {resendTimer > 0 && <TimerText>({resendTimer}с)</TimerText>}
        </ResendButton>

        <VerifyButton 
          onClick={handleVerify} 
          disabled={!isCodeComplete || isVerifying}
        >
          {isVerifying ? 'Проверка...' : 'Подтвердить'}
        </VerifyButton>

        {error && <ErrorMessage>{error}</ErrorMessage>}
      </ContentWrapper>
    </PageContainer>
  );
};

export default VerifyEmailPage;
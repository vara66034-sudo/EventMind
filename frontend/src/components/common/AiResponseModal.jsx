import React, { useEffect, useState } from 'react';
import styled, { keyframes, css } from 'styled-components';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(25, 0, 25, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 30px;
  max-width: 600px;
  width: 100%;
  padding: 40px;
  position: relative;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  animation: ${fadeIn} 0.5s ease-out;
  color: #FFFFFF;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  color: #FFFFFF;
  font-size: 24px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s;
  
  &:hover {
    opacity: 1;
  }
`;

const Title = styled.h2`
  font-size: 24px;
  margin-bottom: 20px;
  background: linear-gradient(90deg, #DFB6B2, #854E6B);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const QuestionText = styled.p`
  font-style: italic;
  color: #DFB6B2;
  margin-bottom: 30px;
  font-size: 16px;
  opacity: 0.8;
`;

const AnswerText = styled.div`
  font-size: 18px;
  line-height: 1.6;
  color: #FFFFFF;
  white-space: pre-wrap;
  
  ${props => props.isLoading && css`
    color: transparent;
    background: linear-gradient(90deg, #512A59 25%, #854E6B 50%, #512A59 75%);
    background-size: 200% 100%;
    animation: ${shimmer} 1.5s infinite linear;
    -webkit-background-clip: text;
    border-radius: 4px;
  `}
`;

const Sparkles = () => (
  <span role="img" aria-label="sparkles">✨</span>
);

const AiResponseModal = ({ isOpen, onClose, question, answer, isLoading }) => {
  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <CloseButton onClick={onClose}>&times;</CloseButton>
        <Title>
          <Sparkles /> EventMind AI
        </Title>
        {question && <QuestionText>«{question}»</QuestionText>}
        <AnswerText isLoading={isLoading}>
          {isLoading ? 'Генерирую ответ...' : answer || 'Я не смог найти ответ на этот вопрос.'}
        </AnswerText>
      </ModalContent>
    </ModalOverlay>
  );
};

export default AiResponseModal;

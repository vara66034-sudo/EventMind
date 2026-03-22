import React from 'react';
import styled from 'styled-components';

const StyledButton = styled.button`
  display: inline-block;
  padding: 12px 32px;
  font-size: 24px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  text-decoration: none;
  
  /* Варианты */
  ${({ variant }) => variant === 'primary' && `
    background: linear-gradient(135deg, #854E6B 0%, #512A59 100%);
    color: #FFFFFF;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(133, 78, 107, 0.4);
    }
  `}
  
  ${({ variant }) => variant === 'secondary' && `
    background: transparent;
    color: #854E6B;
    border: 2px solid #854E6B;
    
    &:hover {
      background: #854E6B;
      color: #FFFFFF;
    }
  `}
  
  ${({ variant }) => variant === 'white' && `
    background: #FFFFFF;
    color: #512A59;
    
    &:hover {
      background: #D9D9D9;
    }
  `}
  
  /* Размеры */
  ${({ size }) => size === 'small' && `
    padding: 8px 20px;
    font-size: 16px;
  `}
  
  ${({ size }) => size === 'large' && `
    padding: 16px 40px;
    font-size: 28px;
  `}
  
  /* Disabled */
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  /* Адаптивность */
  @media (max-width: 768px) {
    padding: 10px 24px;
    font-size: 18px;
  }
`;

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  onClick,
  disabled = false,
  type = 'button',
  className 
}) => {
  return (
    <StyledButton
      type={type}
      variant={variant}
      size={size}
      onClick={onClick}
      disabled={disabled}
      className={className}
    >
      {children}
    </StyledButton>
  );
};

export default Button;
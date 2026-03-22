import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  position: relative;
  display: inline-block;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #FBE4D8;
  color: #512A59;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #DFB6B2;
  }
`;

const Dropdown = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
`;

const Option = styled.div`
  padding: 12px 20px;
  color: #512A59;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #FBE4D8;
  }
  
  ${({ isSelected }) => isSelected && `
    background: #DFB6B2;
    font-weight: 600;
  `}
`;

const cities = [
  'Москва',
  'Санкт-Петербург',
  'Екатеринбург',
  'Казань',
  'Новосибирск',
  'Нижний Новгород',
  'Краснодар',
  'Сочи',
  'Владивосток',
  'Онлайн',
];

const CitySelector = ({ onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCity, setSelectedCity] = useState('Все города');

  const handleSelect = (city) => {
    setSelectedCity(city);
    setIsOpen(false);
    if (onSelect) {
      onSelect(city);
    }
  };

  return (
    <Container>
        <Button onClick={() => setIsOpen(!isOpen)}>
        {selectedCity}
        <span>{isOpen ? '▲' : '▼'}</span>
        </Button>
      
      {isOpen && (
        <Dropdown>
          {cities.map((city) => (
            <Option
              key={city}
              isSelected={selectedCity === city}
              onClick={() => handleSelect(city)}
            >
              {city}
            </Option>
          ))}
        </Dropdown>
      )}
    </Container>
  );
};

export default CitySelector;
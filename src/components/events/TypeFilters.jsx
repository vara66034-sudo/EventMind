import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  background: #FFFFFF;
  padding: 15px 0;
  border-bottom: 1px solid #D9D9D9;
`;

const FiltersWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
`;

const FilterItem = styled.button`
  padding: 8px 16px;
  background: transparent;
  color: #512A59;
  border: 1px solid #D9D9D9;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #FBE4D8;
    border-color: #854E6B;
  }
  
  ${({ isActive }) => isActive && `
    background: #854E6B;
    color: #FFFFFF;
    border-color: #854E6B;
  `}
`;

const types = [
  'Все мероприятия',
  'Концерты',
  'Театр',
  'Выставки',
  'Спорт',
  'Образование',
  'Детям',
];

const TypeFilters = ({ activeType, onTypeChange }) => {
  return (
    <Container>
      <FiltersWrapper>
        {types.map((type) => (
          <FilterItem
            key={type}
            isActive={activeType === type}
            onClick={() => onTypeChange(type)}
          >
            {type}
          </FilterItem>
        ))}
      </FiltersWrapper>
    </Container>
  );
};

export default TypeFilters;
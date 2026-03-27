import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin: 20px 0;
`;

const FilterButton = styled.button`
  padding: 10px 20px;
  background: ${({ isActive }) => (isActive ? '#854E6B' : '#FBE4D8')};
  color: ${({ isActive }) => (isActive ? '#FFFFFF' : '#512A59')};
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

const filters = [
  { id: 'all', label: 'Все' },
  { id: 'concerts', label: 'Концерты' },
  { id: 'theater', label: 'Театр' },
  { id: 'exhibitions', label: 'Выставки' },
  { id: 'sports', label: 'Спорт' },
  { id: 'online', label: 'Онлайн' },
];

const EventFilters = ({ onFilterChange }) => {
  const [activeFilter, setActiveFilter] = useState('all');

  const handleFilter = (filterId) => {
    setActiveFilter(filterId);
    if (onFilterChange) {
      onFilterChange(filterId);
    }
  };

  return (
    <Container>
      {filters.map((filter) => (
        <FilterButton
          key={filter.id}
          isActive={activeFilter === filter.id}
          onClick={() => handleFilter(filter.id)}
        >
          {filter.label}
        </FilterButton>
      ))}
    </Container>
  );
};

export default EventFilters;

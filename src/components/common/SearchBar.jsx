import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.form`
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 20px;
  padding: 10px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
`;

const Input = styled.input`
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: #512A59;
  background: transparent;
  
  &::placeholder {
    color: #D9D9D9;
  }
`;

const SearchButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: #854E6B;
  
  &:hover {
    color: #512A59;
  }
`;

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(query);
    }
  };

  return (
    <Container onSubmit={handleSubmit}>
      <Input
        type="text"
        placeholder="Поиск мероприятий..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <SearchButton type="submit">Поиск</SearchButton>
    </Container>
  );
};

export default SearchBar;
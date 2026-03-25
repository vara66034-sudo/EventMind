import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import CitySelector from '../common/CitySelector';
import SearchBar from '../common/SearchBar';

const HeaderContainer = styled.header`
  background: #190019;
  padding: 15px 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Nav = styled.nav`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  
  @media (max-width: 768px) {
    flex-wrap: wrap;
    padding: 0 20px;
    gap: 15px;
  }
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const ProfileLink = styled(Link)`
  color: #FFFFFF;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    color: #DFB6B2;
  }
`;

const Divider = styled.span`
  color: #512A59;
`;

const Header = () => {
  return (
    <HeaderContainer>
      <Nav>
        <LeftSection>
          <CitySelector />
          <SearchBar />
        </LeftSection>
        <RightSection>
          <ProfileLink to="/">События</ProfileLink>
          <Divider>/</Divider>
          <ProfileLink to="/profile">Мой профиль</ProfileLink>
          <Divider>/</Divider>
          <ProfileLink to="/login">Войти</ProfileLink>
        </RightSection>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;
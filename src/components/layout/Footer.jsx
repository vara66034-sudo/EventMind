import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background: #180018;
  color: #FFFFFF;
  padding: 30px 0;
  margin-top: 50px;
  text-align: center;
`;

const Text = styled.p`
  color: #D9D9D9;
  font-size: 14px;
  margin: 5px 0;
`;

const Footer = () => {
  return (
    <FooterContainer>
      <Text>© 2024 EventMind. Все права защищены.</Text>
      <Text>Сделано с ❤️ для твоих событий</Text>
    </FooterContainer>
  );
};

export default Footer;
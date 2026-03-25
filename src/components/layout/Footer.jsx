import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background: #190019;
  color: #FFFFFF;
  padding: 30px 0;
  margin-top: 50px;
  text-align: center;
`;

const Text = styled.p`
  color: #FFFFFF;
  font-size: 14px;
  margin: 5px 0;
`;

const Footer = () => {
  return (
    <FooterContainer>
      <Text>© 2026 EventMind. Все права защищены.</Text>
      <Text>Сделано с ❤️ для твоих событий</Text>
    </FooterContainer>
  );
};

export default Footer;
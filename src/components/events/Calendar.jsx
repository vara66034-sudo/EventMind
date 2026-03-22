import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  margin: 40px 0;
  padding: 0 40px;
  
  @media (max-width: 768px) {
    padding: 0 20px;
  }
`;

const CalendarTitle = styled.h2`
  color: #180018;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 700;
`;

const CalendarWrapper = styled.div`
  background: #D9D9D9;
  border-radius: 12px;
  padding: 20px 30px;
`;

const CalendarHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const NavButton = styled.button`
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 24px;
  color: #180018;
  padding: 5px 10px;
  
  &:hover {
    color: #854E6B;
  }
`;

const DaysRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
`;

const DayColumn = styled.div`
  flex: 1;
  text-align: center;
`;

const DayName = styled.div`
  font-size: 12px;
  color: #512A59;
  margin-bottom: 8px;
  font-weight: 500;
`;

const DayNumber = styled.div`
  font-size: 20px;
  color: #180018;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${({ isToday }) =>
    isToday &&
    `
    background: #854E6B;
    color: #FFFFFF;
    font-weight: 600;
  `}
  
  ${({ isSelected }) =>
    isSelected &&
    `
    background: #FFFFFF;
    color: #512A59;
  `}
  
  &:hover {
    background: #FFFFFF;
  }
`;

const Divider = styled.div`
  width: 1px;
  height: 30px;
  background: #512A59;
  margin: 0 10px;
`;

const Calendar = () => {
  const [selectedDay, setSelectedDay] = useState(null);
  const today = new Date().getDate();

  const weekDays = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'];
  
  const getCurrentWeekDays = () => {
    const curr = new Date();
    const week = [];
    const firstDayOfWeek = curr.getDate() - curr.getDay() + 1;
    
    for (let i = 0; i < 7; i++) {
      week.push(firstDayOfWeek + i);
    }
    
    return week;
  };

  const days = getCurrentWeekDays();

  return (
    <Container>
      <CalendarTitle>Календарь событий</CalendarTitle>
      <CalendarWrapper>
        <CalendarHeader>
          <NavButton>‹</NavButton>
          <DaysRow>
            {weekDays.map((day, index) => (
              <DayColumn key={day}>
                <DayName>{day}</DayName>
                <DayNumber
                  isToday={days[index] === today}
                  isSelected={selectedDay === days[index]}
                  onClick={() => setSelectedDay(days[index])}
                >
                  {days[index]}
                </DayNumber>
              </DayColumn>
            ))}
          </DaysRow>
          <NavButton>›</NavButton>
        </CalendarHeader>
      </CalendarWrapper>
    </Container>
  );
};

export default Calendar;
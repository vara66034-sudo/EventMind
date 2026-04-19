import React, { useState, useEffect, useMemo, useCallback } from 'react';
import styled from 'styled-components';
import { scheduleAPI } from '../../services/api';

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
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ExportButton = styled.button`
  background: #854E6B;
  color: #FFFFFF;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #512A59;
  }
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
  position: relative;
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
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
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
  
  ${({ isBusy }) =>
    isBusy &&
    `
    border: 2px solid #854E6B;
    background: rgba(133, 78, 107, 0.15);
    font-weight: 600;
  `}
  
  &:hover {
    background: #FFFFFF;
  }
`;

const SelectedDayEvents = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: #FFFFFF;
  border-radius: 12px;
  max-height: 200px;
  overflow-y: auto;
`;

const EventItem = styled.div`
  padding: 8px 0;
  border-bottom: 1px solid #D9D9D9;
  font-size: 14px;
  color: #180018;
  
  &:last-child {
    border-bottom: none;
  }
`;

const EventTime = styled.span`
  font-weight: 600;
  color: #512A59;
  margin-right: 8px;
`;

const Calendar = () => {
  const [selectedDay, setSelectedDay] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);

  const today = new Date();
  const todayDate = today.getDate();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();

  const weekDays = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'];
  
  const getCurrentWeekDays = useCallback(() => {
    const curr = new Date();
    const week = [];
    const firstDayOfWeek = curr.getDate() - (curr.getDay() === 0 ? 6 : curr.getDay() - 1);
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(curr.getFullYear(), curr.getMonth(), firstDayOfWeek + i);
      week.push({
        day: firstDayOfWeek + i,
        dateKey: date.toISOString().split('T')[0],
        fullDate: date
      });
    }
    return week;
  }, []);

  const days = useMemo(() => getCurrentWeekDays(), [getCurrentWeekDays]);

  const eventsByDate = useMemo(() => {
    return schedule.reduce((acc, event) => {
      if (!event.start) return acc;
      const dateKey = event.start.split('T')[0];
      if (!acc[dateKey]) acc[dateKey] = [];
      acc[dateKey].push(event);
      return acc;
    }, {});
  }, [schedule]);

  const loadSchedule = useCallback(async () => {
    try {
      setLoading(true);
      const response = await scheduleAPI.getSchedule('planned');
      setSchedule(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading schedule:', error);
      setSchedule([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSchedule();
  }, [loadSchedule]);

  const handleExportICS = useCallback(async () => {
    try {
      await scheduleAPI.exportICS();
    } catch (error) {
      console.error('Error exporting ICS:', error);
      alert('Не удалось экспортировать календарь');
    }
  }, []);

  const formatTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  const selectedDayEvents = selectedDay 
    ? eventsByDate[days.find(d => d.day === selectedDay)?.dateKey] || []
    : [];

  return (
    <Container>
      <CalendarTitle>
        Календарь событий
        <ExportButton onClick={handleExportICS}>📥 Скачать .ics</ExportButton>
      </CalendarTitle>
      <CalendarWrapper>
        <CalendarHeader>
          <NavButton>‹</NavButton>
          <DaysRow>
            {weekDays.map((dayName, index) => {
              const dayData = days[index];
              const dayEvents = dayData ? eventsByDate[dayData.dateKey] || [] : [];
              
              return (
                <DayColumn key={dayName}>
                  <DayName>{dayName}</DayName>
                  <DayNumber
                    isToday={dayData?.day === todayDate && currentMonth === today.getMonth()}
                    isSelected={selectedDay === dayData?.day}
                    isBusy={dayEvents.length > 0}
                    onClick={() => dayData && setSelectedDay(dayData.day)}
                  >
                    {dayData?.day}
                  </DayNumber>
                </DayColumn>
              );
            })}
          </DaysRow>
          <NavButton>›</NavButton>
        </CalendarHeader>

        {selectedDay && selectedDayEvents.length > 0 && (
          <SelectedDayEvents>
            {selectedDayEvents.map((event, idx) => (
              <EventItem key={idx}>
                <EventTime>{formatTime(event.start)}</EventTime>
                {event.name}
              </EventItem>
            ))}
          </SelectedDayEvents>
        )}
      </CalendarWrapper>
    </Container>
  );
};

export default Calendar;

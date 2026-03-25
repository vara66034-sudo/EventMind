import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import TypeFilters from '../components/events/TypeFilters';
import scheduleAPI from '../api/schedule';

// Основной контейнер
const PageContainer = styled.div`
  min-height: 100vh;
  background: #FFFFFF;
`;

// Фиолетовая шапка профиля
const ProfileHeader = styled.div`
  background: #512A59;
  padding: 40px 40px 0 40px;
  min-height: auto;
  margin-top: 0;
  
  @media (max-width: 768px) {
    padding: 20px 20px 0 20px;
  }
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  
  @media (max-width: 768px) {
    padding: 0 20px;
  }
`;

// Верхняя часть профиля
const ProfileTop = styled.div`
  position: relative;
  display: flex;
  gap: 0;
  margin-bottom: 40px;
  padding-left: 0;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 20px;
  }
`;

// Левая колонка (информация о пользователе)
const ProfileInfo = styled.div`
  position: relative;
  width: 400px;
  background: #FBE4D8;
  border-radius: 0 24px 24px 0;
  padding: 50px;
  text-align: center;
  color: #180018;
  z-index: 10;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  margin-right: -30px;
  margin-left: 40px;
  
  @media (max-width: 1550px) {
    width: 100%;
    margin-right: 0;
    margin-bottom: 20px;
    margin-left: 0;
    border-radius: 24px;
  }
`;

// Аватар
const Avatar = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #D9D9D9;
  margin: 0 auto 20px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #854E6B;
`;

const UserName = styled.h1`
  font-size: 24px;
  margin: 0 0 15px 0;
  color: #180018;
  font-weight: 700;
`;

const UserInfo = styled.p`
  font-size: 14px;
  color: #512A59;
  margin: 8px 0;
`;

const EditButton = styled(Link)`
  margin-top: 20px;
  padding: 10px 30px;
  background: #FFFFFF;
  color: #512A59;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  cursor: pointer;
  
  &:hover {
    background: #DFB6B2;
  }
`;

// Правая колонка (календарь)
const ProfileCalendar = styled.div`
  flex: 1;
  background: #512A59;
  border-radius: 0 24px 24px 0;
  padding: 20px 25px 25px 40px;
  color: #180018;
  margin-left: 0;
  max-width: 700px;
  
  @media (max-width: 768px) {
    padding: 20px;
    border-radius: 24px;
    max-width: 100%;
  }
`;

// Календарь
const CalendarMonth = styled.div`
  width: 100%;
`;

const CalendarHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
`;

const CalendarTitle = styled.h2`
  font-size: 24px;
  margin: 0;
  color: #180018;
  font-weight: 700;
  text-align: center;
  flex: 1;
`;

const NavButton = styled.button`
  background: transparent;
  border: 2px solid #180018;
  color: #180018;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &:hover {
    background: #180018;
    color: #FFFFFF;
  }
`;

const WeekDays = styled.div`
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
  margin-bottom: 8px;
`;

const WeekDay = styled.div`
  text-align: center;
  color: #180018;
  font-size: 12px;
  font-weight: 700;
  padding: 5px 0;
`;

const DaysGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 50px;
`;

const Day = styled.div`
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #180018;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
  ${({ isEmpty }) =>
    isEmpty &&
    `
    visibility: hidden;
    cursor: default;
  `}
  
  ${({ isToday }) =>
    isToday &&
    `
    border: 2px solid #180018;
    border-radius: 50%;
    font-weight: 700;
  `}
  
  ${({ isSelected }) =>
    isSelected &&
    `
    border: 2px solid #180018;
    border-radius: 50%;
    font-weight: 700;
  `}
  
  ${({ isBusy }) =>
    isBusy &&
    `
    border: 2px solid #854E6B;
    border-radius: 50%;
    font-weight: 700;
    background: rgba(133, 78, 107, 0.1);
  `}
  
  &:hover {
    ${({ hasEvent }) => !hasEvent && `
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50%;
    `}
  }
`;

// Белый блок с интересами и рекомендациями
const WhiteSection = styled.div`
  background: #FFFFFF;
  padding: 40px;
  margin-bottom: 0;
  margin-top: 0;
  color: #180018;
  position: relative;
  z-index: 20;
  min-height: 400px;
  
  @media (max-width: 768px) {
    padding: 20px;
  }
`;

const SectionTitle = styled.h2`
  font-size: 25px;
  margin: 0 0 20px 0;
  color: #190019;
  padding-bottom: 10px;
  border-bottom: 2px solid #D9D9D9;
  font-weight: 700;
`;

// Интересы
const InterestsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 30px;
`;

const InterestTag = styled.div`
  background: #DFB6B2;
  color: #512A59;
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const RemoveButton = styled.span`
  cursor: pointer;
  font-weight: bold;
  margin-left: 8px;
  
  &:hover {
    color: #180018;
  }
`;

const AddInterestButton = styled.button`
  background: #854E6B;
  color: #FFFFFF;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  
  &:hover {
    background: #512A59;
  }
`;

// Рекомендации
const RecommendationsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
`;

const RecommendationCard = styled.div`
  background: #854E6B;
  border-radius: 16px;
  height: 120px;
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

// Загрузка
const Loader = styled.div`
  text-align: center;
  padding: 60px;
  color: #FFFFFF;
  font-size: 20px;
`;

// Модальное окно для добавления события
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const Modal = styled.div`
  background: #FFFFFF;
  border-radius: 24px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  color: #180018;
`;

const ModalTitle = styled.h3`
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #180018;
`;

const ModalForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const ModalInput = styled.input`
  padding: 12px 15px;
  border: 2px solid #D9D9D9;
  border-radius: 12px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #854E6B;
  }
`;

const ModalButtons = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 10px;
`;

const ModalButton = styled.button`
  flex: 1;
  padding: 12px 20px;
  background: ${({ secondary }) => secondary ? '#D9D9D9' : '#854E6B'};
  color: ${({ secondary }) => secondary ? '#180018' : '#FFFFFF'};
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background: ${({ secondary }) => secondary ? '#DFB6B2' : '#512A59'};
  }
`;

// Список событий дня
const DayEvents = styled.div`
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  font-size: 11px;
  color: #512A59;
  max-width: 100%;
  text-align: center;
`;

const EventItem = styled.div`
  margin: 2px 0;
  font-weight: 500;
`;

const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [interests, setInterests] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [schedule, setSchedule] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '',
    startTime: '09:00',
    endTime: '10:00',
  });
  const [userId] = useState(1);

  // Загрузка данных профиля и расписания
  useEffect(() => {
    loadProfileData();
    loadSchedule();
  }, [currentMonth]);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      
      setUser({
        id: 1,
        name: 'Имя Фамилия',
        email: 'user@example.com',
        friendsCount: 42,
        avatar: null,
      });
      
      setInterests(['Концерты', 'Театр', 'Выставки', 'Спорт', 'Музыка']);
      
      setRecommendations([
        { id: 1, name: 'Рекомендация 1' },
        { id: 2, name: 'Рекомендация 2' },
        { id: 3, name: 'Рекомендация 3' },
        { id: 4, name: 'Рекомендация 4' },
        { id: 5, name: 'Рекомендация 5' },
        { id: 6, name: 'Рекомендация 6' },
      ]);
      
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  // Загрузка расписания с бэкенда
  const loadSchedule = async () => {
    try {
      const startOfWeek = new Date(currentMonth);
      startOfWeek.setDate(currentMonth.getDate() - currentMonth.getDay() + 1);
      
      const response = await scheduleAPI.getSchedule(userId, startOfWeek);
      
      if (response.success) {
        setSchedule(response.data);
      }
    } catch (error) {
      console.error('Error loading schedule:', error);
      // Тестовые данные при ошибке
      setSchedule({
        '2024-04-15': [{ start: '2024-04-15T10:00:00', end: '2024-04-15T12:00:00', title: 'Встреча' }],
        '2024-04-18': [{ start: '2024-04-18T14:00:00', end: '2024-04-18T16:00:00', title: 'Обучение' }],
      });
    }
  };

  // Обработка клика по дате
  const handleDayClick = (day) => {
    if (!day) return;
    
    const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
    const dateKey = date.toISOString().split('T')[0];
    
    setSelectedDate(date);
    
    // Сбрасываем форму для нового события
    setNewEvent({
      title: '',
      startTime: '09:00',
      endTime: '10:00',
    });
    setIsModalOpen(true);
  };

  // Добавление нового события
  const handleAddEvent = async (e) => {
    e.preventDefault();
    
    if (!selectedDate) return;
    
    try {
      const [startHours, startMinutes] = newEvent.startTime.split(':');
      const [endHours, endMinutes] = newEvent.endTime.split(':');
      
      const start = new Date(selectedDate);
      start.setHours(parseInt(startHours), parseInt(startMinutes));
      
      const end = new Date(selectedDate);
      end.setHours(parseInt(endHours), parseInt(endMinutes));
      
      const response = await scheduleAPI.addBusySlot(
        userId,
        start,
        end,
        newEvent.title || 'Занят'
      );
      
      if (response.success) {
        await loadSchedule();
        setIsModalOpen(false);
        alert('Событие добавлено!');
      }
    } catch (error) {
      console.error('Error adding event:', error);
      alert('Ошибка добавления события');
    }
  };

  // Форматирование времени
  const formatTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleRemoveInterest = (interest) => {
    setInterests(interests.filter(i => i !== interest));
  };

  const handleAddInterest = () => {
    const newInterest = prompt('Введите интерес:');
    if (newInterest) {
      setInterests([...interests, newInterest]);
    }
  };

  // Генерация дней месяца
  const generateMonthDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    const days = [];
    
    const startDayOfWeek = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
    
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push({ day: null, isEmpty: true });
    }
    
    for (let day = 1; day <= lastDay.getDate(); day++) {
      days.push({ day, isEmpty: false });
    }
    
    return days;
  };

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const today = new Date().getDate();
  const days = generateMonthDays();

  if (loading) {
    return (
      <PageContainer>
        <TypeFilters activeType="" onTypeChange={() => {}} />
        <Loader>Загрузка профиля...</Loader>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Фильтры типов мероприятий */}
      <TypeFilters activeType="" onTypeChange={() => {}} />
      
      {/* Фиолетовая шапка профиля */}
      <ProfileHeader>
        <ContentWrapper>
          <ProfileTop>
            {/* Информация о пользователе */}
            <ProfileInfo>
              <Avatar>
                {user?.avatar ? (
                  <img src={user.avatar} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  '👤'
                )}
              </Avatar>
              
              <UserName>{user?.name}</UserName>
              
              <UserInfo>Друзья: {user?.friendsCount}</UserInfo>
              <UserInfo>{user?.email}</UserInfo>
              
              <EditButton to="/profile/edit">
                ✏️ Редактировать
              </EditButton>
            </ProfileInfo>

            {/* Календарь */}
            <ProfileCalendar>
              <CalendarMonth>
                <CalendarHeader>
                  <NavButton onClick={handlePrevMonth}>‹</NavButton>
                  <CalendarTitle>
                    {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                  </CalendarTitle>
                  <NavButton onClick={handleNextMonth}>›</NavButton>
                </CalendarHeader>

                <WeekDays>
                  {weekDays.map((day) => (
                    <WeekDay key={day}>{day}</WeekDay>
                  ))}
                </WeekDays>

                <DaysGrid>
                  {days.map((item, index) => {
                    const dateKey = item.day 
                      ? new Date(currentMonth.getFullYear(), currentMonth.getMonth(), item.day).toISOString().split('T')[0]
                      : null;
                    
                    const dayEvents = item.day ? schedule[dateKey] : [];
                    
                    return (
                      <Day
                        key={index}
                        isEmpty={item.isEmpty}
                        isToday={!item.isEmpty && item.day === today && currentMonth.getMonth() === new Date().getMonth()}
                        isSelected={!item.isEmpty && selectedDate?.getDate() === item.day}
                        isBusy={!item.isEmpty && dayEvents?.length > 0}
                        onClick={() => !item.isEmpty && handleDayClick(item.day)}
                      >
                        {item.day}
                        {!item.isEmpty && dayEvents?.length > 0 && (
                          <DayEvents>
                            {dayEvents.slice(0, 2).map((event, i) => (
                              <EventItem key={i}>
                                {formatTime(event.start)} - {event.title}
                              </EventItem>
                            ))}
                            {dayEvents.length > 2 && (
                              <EventItem>+{dayEvents.length - 2} ещё</EventItem>
                            )}
                          </DayEvents>
                        )}
                      </Day>
                    );
                  })}
                </DaysGrid>
              </CalendarMonth>
            </ProfileCalendar>
          </ProfileTop>
        </ContentWrapper>
      </ProfileHeader>

      {/* Белый блок с интересами и рекомендациями */}
      <ContentWrapper>
        <WhiteSection>
          <SectionTitle>Ваши интересы</SectionTitle>
          
          <InterestsGrid>
            {interests.map((interest, index) => (
              <InterestTag key={index}>
                {interest}
                <RemoveButton onClick={() => handleRemoveInterest(interest)}>
                  ✕
                </RemoveButton>
              </InterestTag>
            ))}
            <AddInterestButton onClick={handleAddInterest}>
              + Добавить
            </AddInterestButton>
          </InterestsGrid>

          <SectionTitle>Рекомендации для вас</SectionTitle>
          
          <RecommendationsGrid>
            {recommendations.map((rec) => (
              <RecommendationCard key={rec.id} />
            ))}
          </RecommendationsGrid>
        </WhiteSection>
      </ContentWrapper>

      {/* Модальное окно для добавления события */}
      {isModalOpen && selectedDate && (
        <ModalOverlay onClick={() => setIsModalOpen(false)}>
          <Modal onClick={(e) => e.stopPropagation()}>
            <ModalTitle>
              {schedule[selectedDate.toISOString().split('T')[0]]?.length > 0 
                ? `События на ${selectedDate.toLocaleDateString('ru-RU')}` 
                : `Добавить событие на ${selectedDate.toLocaleDateString('ru-RU')}`}
            </ModalTitle>
            
            {/* Показываем существующие события */}
            {schedule[selectedDate.toISOString().split('T')[0]]?.length > 0 && (
              <div style={{ marginBottom: '20px', padding: '10px', background: '#FBE4D8', borderRadius: '12px' }}>
                {schedule[selectedDate.toISOString().split('T')[0]].map((event, i) => (
                  <div key={i} style={{ margin: '5px 0', fontSize: '14px' }}>
                    <strong>{formatTime(event.start)} - {formatTime(event.end)}</strong>
                    <br />
                    {event.title}
                  </div>
                ))}
              </div>
            )}
            
            {/* Форма добавления нового события */}
            <ModalForm onSubmit={handleAddEvent}>
              <ModalInput
                type="text"
                placeholder="Название события (опционально)"
                value={newEvent.title}
                onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
              />
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <ModalInput
                  type="time"
                  value={newEvent.startTime}
                  onChange={(e) => setNewEvent({ ...newEvent, startTime: e.target.value })}
                />
                <ModalInput
                  type="time"
                  value={newEvent.endTime}
                  onChange={(e) => setNewEvent({ ...newEvent, endTime: e.target.value })}
                />
              </div>
              
              <ModalButtons>
                <ModalButton type="button" secondary onClick={() => setIsModalOpen(false)}>
                  Отмена
                </ModalButton>
                <ModalButton type="submit">
                  Добавить
                </ModalButton>
              </ModalButtons>
            </ModalForm>
          </Modal>
        </ModalOverlay>
      )}
    </PageContainer>
  );
};

export default ProfilePage;
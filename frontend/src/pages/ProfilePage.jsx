import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { scheduleAPI, userAPI } from '../services/api';
import { AVAILABLE_TAGS } from '../constants/tags';

const PageContainer = styled.div`
  min-height: 100vh;
  background: #FFFFFF;
`;

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
  gap: 10px;
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
  border-radius: 50%;
  
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
    font-weight: 700;
  `}
  
  ${({ isSelected }) =>
    isSelected &&
    `
    background: #FFFFFF;
    font-weight: 700;
  `}
  
  ${({ isBusy }) =>
    isBusy &&
    `
    border: 2px solid #854E6B;
    background: rgba(133, 78, 107, 0.15);
    font-weight: 600;
  `}
  
  &:hover {
    ${({ isEmpty }) => !isEmpty && `
      background: rgba(255, 255, 255, 0.15);
    `}
  }
`;

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

const TabContainer = styled.div`
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  border-bottom: 2px solid #D9D9D9;
`;

const TabButton = styled.button`
  padding: 12px 24px;
  background: transparent;
  color: #512A59;
  border: none;
  border-bottom: ${({ isActive }) => isActive ? '3px solid #854E6B' : '3px solid transparent'};
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: -2px;
  
  &:hover {
    color: #854E6B;
  }
`;

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

const Loader = styled.div`
  text-align: center;
  padding: 60px;
  color: #FFFFFF;
  font-size: 20px;
`;

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
  max-width: 500px;
  width: 90%;
  color: #180018;
  max-height: 85vh;
  overflow-y: auto;
`;

const ModalTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 20px;
  color: #180018;
`;

const ModalForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #D9D9D9;
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

const EventList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
`;

const EventListItem = styled.div`
  background: #FBE4D8;
  padding: 12px 15px;
  border-radius: 12px;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 20px;
  color: #512A59;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
`;

const EmptyText = styled.p`
  font-size: 18px;
  margin: 0 0 10px 0;
  color: #180018;
  font-weight: 600;
`;

const EmptySubtext = styled.p`
  font-size: 14px;
  color: #854E6B;
  margin: 0;
`;

const FavoritesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
`;

const FavoriteCard = styled.div`
  background: #FBE4D8;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
`;

const FavoriteTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #180018;
  font-size: 18px;
  font-weight: 700;
`;

const FavoriteInfo = styled.p`
  color: #512A59;
  font-size: 14px;
  margin: 6px 0;
`;

const TagSelectorGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
  margin: 20px 0;
  max-height: 300px;
  overflow-y: auto;
  padding: 5px;
`;

const TagOption = styled.div`
  background: #FBE4D8;
  color: #512A59;
  padding: 10px 15px;
  border-radius: 16px;
  font-size: 13px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  
  &:hover {
    background: #DFB6B2;
  }
  
  ${({ isSelected }) =>
    isSelected &&
    `
    background: #854E6B;
    color: #FFFFFF;
    border-color: #FFFFFF;
  `}
`;

const parseLocalDateTime = (value) => {
  if (!value) return null;
  if (value instanceof Date) return value;

  const cleanValue = String(value)
    .replace(' ', 'T')
    .replace(/\.\d+/, '')
    .replace(/Z$/, '')
    .replace(/([+-]\d{2}:\d{2})$/, '');

  const [datePart, timePart = '00:00:00'] = cleanValue.split('T');
  const [year, month, day] = datePart.split('-').map(Number);
  const [hours = 0, minutes = 0, seconds = 0] = timePart.split(':').map(Number);

  return new Date(year, month - 1, day, hours, minutes, seconds);
};

const toLocalDateKey = (value) => {
  const date = value instanceof Date ? value : parseLocalDateTime(value);
  if (!date || Number.isNaN(date.getTime())) return null;

  const pad = (num) => String(num).padStart(2, '0');

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
};

const ProfilePage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState({
    id: 1,
    name: 'Имя Фамилия',
    email: 'user@example.com',
    friendsCount: 42,
    avatar: null,
  });
  const [interests, setInterests] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [aiAdvice, setAiAdvice] = useState(null);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [schedule, setSchedule] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [activeTab, setActiveTab] = useState('calendar');
  const [selectedDate, setSelectedDate] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAddTagModalOpen, setIsAddTagModalOpen] = useState(false);
  const [selectedNewTags, setSelectedNewTags] = useState([]);
  const [newEvent, setNewEvent] = useState({
    title: '',
    startTime: '09:00',
    endTime: '10:00',
  });

  const userId = useMemo(() => {
    const auth = localStorage.getItem('auth');
    return auth ? JSON.parse(auth).userId : null;
  }, []);

  useEffect(() => {
    loadProfileData();
    loadSchedule();
    loadFavorites();
    loadRecommendations();
  }, [currentMonth]);

  const loadProfileData = async () => {
    if (!userId) {
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      const response = await userAPI.getProfile(userId);
      
      if (response && response.success) {
        const profile = response.data;
        setUser({
          id: profile.id,
          name: profile.name,
          email: profile.email,
          friendsCount: profile.friends_count || 0,
          avatar: profile.avatar,
        });

        setInterests(profile.interests || []);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      setInterests([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSchedule = useCallback(async () => {
    console.log('Loading schedule for userId:', userId);
    if (!userId || userId === 'null' || userId === 'undefined') {
      setSchedule([]);
      return;
    }
    try {
      const response = await scheduleAPI.getSchedule(userId, 'planned');
      
      const scheduleData = Array.isArray(response)
        ? response
        : response?.success
          ? response.data
          : [];

      setSchedule(scheduleData || []);
    } catch (error) {
      console.error('Error loading schedule:', error);
      setSchedule([]);
    }
  }, [userId]);

  const loadFavorites = useCallback(async () => {
    if (!userId) {
      setFavorites([]);
      return;
    }
    try {
      const response = await scheduleAPI.getFavorites(userId);
      
      const favoritesData = Array.isArray(response)
        ? response
        : response?.success
          ? response.data
          : [];

      setFavorites(favoritesData || []);
    } catch (error) {
      console.error('Error loading favorites:', error);
      setFavorites([]);
    }
  }, [userId]);

  const loadRecommendations = useCallback(async () => {
    if (!userId || userId === 'null' || userId === 'undefined') {
      setRecommendations([]);
      setAiAdvice(null);
      return;
    }

    try {
      setRecommendationsLoading(true);

      const response = await userAPI.getRecommendationsWithSchedule(userId, 10);

      if (response && response.success) {
        setRecommendations(Array.isArray(response.data) ? response.data : []);
        setAiAdvice(response.ai_advice || null);
      } else {
        console.error('Recommendations error:', response?.error);
        setRecommendations([]);
        setAiAdvice(null);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      setRecommendations([]);
      setAiAdvice(null);
    } finally {
      setRecommendationsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (!isModalOpen) {
      loadSchedule();
    }
  }, [isModalOpen, loadSchedule]);

  const scheduleByDate = useMemo(() => {
    return schedule.reduce((acc, event) => {
      if (!event.start) return acc;

      const dateKey = toLocalDateKey(event.start);
      if (!dateKey) return acc;

      if (!acc[dateKey]) acc[dateKey] = [];
      acc[dateKey].push(event);

      return acc;
    }, {});
  }, [schedule]);

  const handleDayClick = (day) => {
    if (!day) return;
    const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
    setSelectedDate(date);
    setNewEvent({
      title: '',
      startTime: '09:00',
      endTime: '10:00',
    });
    setIsModalOpen(true);
  };

  const handleAddEvent = async (e) => {
    e.preventDefault();
    if (!selectedDate) return;
    
    try {
      const [startHours, startMinutes] = newEvent.startTime.split(':').map(Number);
      const [endHours, endMinutes] = newEvent.endTime.split(':').map(Number);
      
      const start = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        selectedDate.getDate(),
        startHours,
        startMinutes,
        0,
        0
      );
      
      const end = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        selectedDate.getDate(),
        endHours,
        endMinutes,
        0,
        0
      );

      if (userId) {
        await scheduleAPI.addPersonalEvent(
          userId,
          newEvent.title || 'Занят',
          start,
          end,
          '',
          ''
        );
      }
      
      setIsModalOpen(false);
      await loadSchedule();
      await loadRecommendations();
    } catch (error) {
      console.error('Error adding event:', error);
      alert('Ошибка добавления события');
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return '';

    const date = parseLocalDateTime(isoString);
    if (!date || Number.isNaN(date.getTime())) return '';

    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleRemoveInterest = async (interest) => {
    try {
      const newInterests = interests.filter(i => i !== interest);

      if (userId) {
        await userAPI.updateProfile(userId, { interests: newInterests });
      }
      
      setInterests(newInterests);
      await loadRecommendations();
    } catch (error) {
      console.error('Error removing interest:', error);
      alert('Не удалось удалить интерес');
    }
  };

  const remainingTags = useMemo(() => {
    return AVAILABLE_TAGS.filter(tag => !interests.includes(tag));
  }, [interests]);

  const handleOpenAddTagModal = () => {
    setSelectedNewTags([]);
    setIsAddTagModalOpen(true);
  };

  const handleToggleNewTag = (tag) => {
    setSelectedNewTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const handleAddSelectedTags = async () => {
    if (selectedNewTags.length === 0) return;
    
    try {
      const allInterests = [...interests, ...selectedNewTags];

      if (userId) {
        await userAPI.updateProfile(userId, { interests: allInterests });
      }
      
      setInterests(allInterests);
      setIsAddTagModalOpen(false);
      setSelectedNewTags([]);

      await loadRecommendations();
    } catch (error) {
      console.error('Error adding interests:', error);
      alert('Не удалось добавить интересы');
    }
  };

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
  const selectedDateKey = selectedDate ? toLocalDateKey(selectedDate) : null;

  if (loading) {
    return (
      <PageContainer>
        <Loader>Загрузка профиля...</Loader>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <ProfileHeader>
        <ContentWrapper>
          <ProfileTop>
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
                      ? toLocalDateKey(new Date(currentMonth.getFullYear(), currentMonth.getMonth(), item.day))
                      : null;
                    
                    const dayEvents = item.day ? scheduleByDate[dateKey] || [] : [];
                    
                    return (
                      <Day
                        key={index}
                        isEmpty={item.isEmpty}
                        isToday={!item.isEmpty && item.day === today && currentMonth.getMonth() === new Date().getMonth()}
                        isSelected={!item.isEmpty && selectedDate?.getDate() === item.day}
                        isBusy={dayEvents.length > 0}
                        onClick={() => !item.isEmpty && handleDayClick(item.day)}
                      >
                        {item.day}
                      </Day>
                    );
                  })}
                </DaysGrid>
              </CalendarMonth>
            </ProfileCalendar>
          </ProfileTop>
        </ContentWrapper>
      </ProfileHeader>

      <ContentWrapper>
        <WhiteSection>
          <TabContainer>
            <TabButton 
              isActive={activeTab === 'calendar'} 
              onClick={() => setActiveTab('calendar')}
            >
              📅 Календарь
            </TabButton>
            <TabButton 
              isActive={activeTab === 'favorites'} 
              onClick={() => setActiveTab('favorites')}
            >
              ⭐ Избранное
            </TabButton>
          </TabContainer>

          {activeTab === 'calendar' && (
            <>
              <SectionTitle>Рекомендации для вас</SectionTitle>

              {aiAdvice && (
                <div
                  style={{
                    background: '#FBE4D8',
                    color: '#180018',
                    padding: '16px 20px',
                    borderRadius: '16px',
                    marginBottom: '20px',
                    lineHeight: 1.5,
                  }}
                >
                  <strong>Совет AI:</strong> {aiAdvice}
                </div>
              )}

              {recommendationsLoading ? (
                <p style={{ color: '#512A59', marginBottom: '30px' }}>
                  Подбираем рекомендации...
                </p>
              ) : recommendations.length === 0 ? (
                <p style={{ color: '#512A59', marginBottom: '30px' }}>
                  Пока нет подходящих рекомендаций. Добавьте интересы или проверьте, что в базе есть будущие события с тегами.
                </p>
              ) : (
                <RecommendationsGrid>
                  {recommendations.map((rec) => {
                    const event = rec.event || rec;

                    return (
                      <RecommendationCard
                        key={event.id}
                        onClick={() => navigate(`/events/${event.id}`)}
                      >
                        <div style={{ padding: '15px', color: '#fff' }}>
                          <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                            {event.name || event.title}
                          </div>

                          {event.date_begin && (
                            <div style={{ fontSize: '12px', opacity: 0.85, marginBottom: '4px' }}>
                              {new Date(event.date_begin).toLocaleString('ru-RU', {
                                day: '2-digit',
                                month: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </div>
                          )}

                          <div style={{ fontSize: '12px', opacity: 0.85 }}>
                            Совпадение: {Math.round((rec.score || 0) * 100)}%
                          </div>

                          {rec.explanation && (
                            <div style={{ fontSize: '11px', opacity: 0.75, marginTop: '6px' }}>
                              {rec.explanation}
                            </div>
                          )}
                        </div>
                      </RecommendationCard>
                    );
                  })}
                </RecommendationsGrid>
              )}
              
              <div style={{ marginTop: '40px' }}>
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
                  {remainingTags.length > 0 && (
                    <AddInterestButton onClick={handleOpenAddTagModal}>
                      + Добавить
                    </AddInterestButton>
                  )}
                </InterestsGrid>
              </div>
            </>
          )}

          {activeTab === 'favorites' && (
            <>
              <SectionTitle>Мои избранные события</SectionTitle>
              
              {favorites.length === 0 ? (
                <EmptyState>
                  <EmptyIcon>⭐</EmptyIcon>
                  <EmptyText>Избранных событий еще нет</EmptyText>
                  <EmptySubtext>Добавляйте события в избранное, чтобы они появились здесь</EmptySubtext>
                </EmptyState>
              ) : (
                <FavoritesGrid>
                  {favorites.map((event) => (
                    <FavoriteCard key={event.id} onClick={() => navigate(`/events/${event.id}`)} style={{ cursor: 'pointer' }}>
                      <FavoriteTitle>{event.name}</FavoriteTitle>
                      {event.start && (
                        <FavoriteInfo>📅 {formatTime(event.start)}</FavoriteInfo>
                      )}
                      {event.location && (
                        <FavoriteInfo>📍 {event.location}</FavoriteInfo>
                      )}
                    </FavoriteCard>
                  ))}
                </FavoritesGrid>
              )}
            </>
          )}
        </WhiteSection>
      </ContentWrapper>

      {isModalOpen && selectedDate && (
        <ModalOverlay onClick={() => setIsModalOpen(false)}>
          <Modal onClick={(e) => e.stopPropagation()}>
            <ModalTitle>
              {scheduleByDate[selectedDateKey]?.length > 0 
                ? `События на ${selectedDate.toLocaleDateString('ru-RU')}` 
                : `Добавить событие на ${selectedDate.toLocaleDateString('ru-RU')}`}
            </ModalTitle>
            
            {scheduleByDate[selectedDateKey]?.length > 0 ? (
              <EventList>
                {scheduleByDate[selectedDateKey].map((event, i) => (
                  <EventListItem key={i}>
                    <div>
                      <strong>{formatTime(event.start)}</strong>
                      <div style={{ fontSize: '13px', color: '#512A59' }}>{event.name}</div>
                    </div>
                  </EventListItem>
                ))}
              </EventList>
            ) : (
              <p style={{ color: '#512A59', marginBottom: '15px' }}>На этот день событий пока нет.</p>
            )}
            
            <ModalForm onSubmit={handleAddEvent}>
              <ModalInput
                type="text"
                placeholder="Название нового события (опционально)"
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
                  Закрыть
                </ModalButton>
                <ModalButton type="submit">
                  Добавить событие
                </ModalButton>
              </ModalButtons>
            </ModalForm>
          </Modal>
        </ModalOverlay>
      )}

      {isAddTagModalOpen && (
        <ModalOverlay onClick={() => setIsAddTagModalOpen(false)}>
          <Modal onClick={(e) => e.stopPropagation()}>
            <ModalTitle>Добавить интересы</ModalTitle>
            <p style={{ color: '#512A59', fontSize: '14px', marginBottom: '15px' }}>
              Выберите теги из списка ({remainingTags.length} доступно):
            </p>
            
            <TagSelectorGrid>
              {remainingTags.map((tag) => (
                <TagOption
                  key={tag}
                  isSelected={selectedNewTags.includes(tag)}
                  onClick={() => handleToggleNewTag(tag)}
                >
                  {tag}
                </TagOption>
              ))}
            </TagSelectorGrid>
            
            <ModalButtons>
              <ModalButton type="button" secondary onClick={() => setIsAddTagModalOpen(false)}>
                Отмена
              </ModalButton>
              <ModalButton 
                type="button" 
                onClick={handleAddSelectedTags}
                disabled={selectedNewTags.length === 0}
              >
                Добавить ({selectedNewTags.length})
              </ModalButton>
            </ModalButtons>
          </Modal>
        </ModalOverlay>
      )}
    </PageContainer>
  );
};

export default ProfilePage;

"""
Управление расписанием пользователя
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RecurrenceType(Enum):
    """Тип повторения события"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class TimeSlot:
    """Слот времени"""
    start: datetime
    end: datetime
    title: str
    event_id: Optional[int] = None
    recurrence: RecurrenceType = RecurrenceType.NONE


class UserCalendar:
    """
    Управление личным календарём пользователя
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._busy_slots = []  
        self._interests = []
    
    def set_interests(self, interests: List[str]):
        """Сохранить интересы пользователя"""
        self._interests = interests
        logger.info(f"User {self.user_id} interests: {interests}")
    
    def get_interests(self) -> List[str]:
        """Получить интересы пользователя"""
        return self._interests
    
    def add_busy_slot(self, slot: TimeSlot):
        """Добавить занятое время"""
        self._busy_slots.append(slot)
        self._busy_slots.sort(key=lambda x: x.start)
    
    def get_busy_slots(self, start_date: datetime, end_date: datetime) -> List[TimeSlot]:
        """Получить занятые слоты в интервале"""
        return [
            slot for slot in self._busy_slots
            if slot.start < end_date and slot.end > start_date
        ]
    
    def is_available(self, event_date: datetime, duration_hours: int = 2) -> bool:
        """
        Проверить, свободен ли пользователь в указанное время.
        Все даты приводим к naive datetime, чтобы не ломалось сравнение.
        """

        if event_date.tzinfo is not None:
            event_date = event_date.replace(tzinfo=None)

        event_end = event_date + timedelta(hours=duration_hours)

        for slot in self._busy_slots:
            slot_start = slot.start
            slot_end = slot.end

            if slot_start and slot_start.tzinfo is not None:
                slot_start = slot_start.replace(tzinfo=None)

            if slot_end and slot_end.tzinfo is not None:
                slot_end = slot_end.replace(tzinfo=None)

            if not (event_date >= slot_end or event_end <= slot_start):
                return False

        return True
    
    def find_free_slots(self, date: datetime, duration_hours: int = 2, 
                       buffer_before: int = 1, buffer_after: int = 1) -> List[datetime]:
        """
        Найти свободные слоты на определённую дату
        
        Args:
            date: Дата (без времени)
            duration_hours: Длительность события
            buffer_before: Буфер до события (часы)
            buffer_after: Буфер после события (часы)
        
        Returns:
            Список возможных времен начала
        """
        day_start = date.replace(hour=9, minute=0, second=0, microsecond=0)
        day_end = date.replace(hour=22, minute=0, second=0, microsecond=0)
        
        free_slots = []
        current_time = day_start
        
        # Получаем занятые слоты на этот день
        busy = self.get_busy_slots(day_start, day_end)
        
        while current_time + timedelta(hours=duration_hours) <= day_end:
            slot_end = current_time + timedelta(hours=duration_hours)
            is_free = True
            
            for busy_slot in busy:
                if not (slot_end <= busy_slot.start or current_time >= busy_slot.end):
                    is_free = False
                    current_time = busy_slot.end
                    break
            
            if is_free:
                free_slots.append(current_time)
                current_time += timedelta(hours=1)  # шаг 1 час
            else:
                continue
        
        return free_slots
    
    def get_week_schedule(self, start_date: datetime) -> Dict[str, List[Dict]]:
        """Получить расписание на неделю"""
        schedule = {}
        for i in range(7):
            date = start_date + timedelta(days=i)
            busy = self.get_busy_slots(date, date + timedelta(days=1))
            schedule[date.strftime('%Y-%m-%d')] = [
                {
                    'start': slot.start.isoformat(),
                    'end': slot.end.isoformat(),
                    'title': slot.title
                }
                for slot in busy
            ]
        return schedule
    
    def format_schedule_text(self, start_date: datetime) -> str:
        """Сформировать текстовое описание расписания для LLM"""
        schedule = self.get_week_schedule(start_date)
        lines = []
        
        for date, slots in schedule.items():
            if slots:
                lines.append(f"{date}:")
                for slot in slots:
                    start_time = slot['start'][11:16]
                    end_time = slot['end'][11:16]
                    lines.append(f"  - {start_time}-{end_time}: {slot['title']}")
            else:
                lines.append(f"{date}: свободен")
        
        return "\n".join(lines)


# Кэш календарей пользователей
_calendars = {}

def get_user_calendar(user_id: int) -> UserCalendar:
    """Получить календарь пользователя"""
    if user_id not in _calendars:
        _calendars[user_id] = UserCalendar(user_id)
    return _calendars[user_id]

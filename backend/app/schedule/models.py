from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./eventmind.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserSchedule(Base):
    __tablename__ = "user_schedule"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_id = Column(Integer, nullable=True)
    is_personal = Column(Boolean, default=False)
    personal_title = Column(String, nullable=True)
    personal_start = Column(DateTime, nullable=True)
    personal_end = Column(DateTime, nullable=True)
    personal_description = Column(Text, nullable=True)
    personal_location = Column(String, nullable=True)
    status = Column(String, default="planned")
    reminder_sent = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("(is_personal = TRUE AND personal_title IS NOT NULL AND personal_start IS NOT NULL) OR (is_personal = FALSE AND event_id IS NOT NULL)", name="chk_personal_fields"),
        UniqueConstraint("user_id", "event_id", name="uniq_user_platform_event"),
    )

class SchedulePlatformCreate(BaseModel):
    event_id: int

class SchedulePersonalCreate(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    description: Optional[str] = ""
    location: Optional[str] = ""

class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: int
    type: str
    event_id: Optional[int] = None
    name: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = ""
    description: Optional[str] = ""
    status: str
    added_at: datetime

    class Config:
        from_attributes = True
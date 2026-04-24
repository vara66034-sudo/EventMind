from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSchedule(Base):
    __tablename__ = "user_schedule"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(Integer, nullable=True)
    is_personal = Column(Boolean, default=False)
    personal_title = Column(String, nullable=True)
    personal_start = Column(DateTime, nullable=True)
    personal_end = Column(DateTime, nullable=True)
    personal_description = Column(Text, nullable=True)
    personal_location = Column(String, nullable=True)
    status = Column(String, default="planned")
    added_at = Column(DateTime, default=datetime.utcnow)

class UserInterest(Base):
    __tablename__ = "user_interests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    interest = Column(String, nullable=False)

class UserFavorite(Base):
    __tablename__ = "user_favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_id = Column(Integer, nullable=False)
    interaction_type = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

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

# Create tables
Base.metadata.create_all(bind=engine)
from datetime import datetime
from sqlalchemy import VARCHAR, Column, BigInteger, Integer,String, DateTime, ForeignKey, Time
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    language = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    work_schedules = relationship("WorkSchedule", back_populates="user")

class WorkSchedule(Base):
    __tablename__ = 'work_schedules'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time1 = Column(Time, nullable=False)
    end_time1 = Column(Time, nullable=False)
    start_time2 = Column(Time, nullable=True)
    end_time2 = Column(Time, nullable=True)
    start_time3 = Column(Time, nullable=True)
    end_time3 = Column(Time, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="work_schedules")

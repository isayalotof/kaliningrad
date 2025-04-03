from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class ScheduleType(str, enum.Enum):
    """Типы расписаний"""
    REGULAR = "regular"     # Регулярное расписание
    CUSTOM = "custom"       # Особое расписание (праздники, события)
    BLOCKED = "blocked"     # Заблокированное время (технические перерывы)


class Schedule(Base):
    """Модель базового расписания для локации"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    schedule_type = Column(Enum(ScheduleType), default=ScheduleType.REGULAR)
    
    # JSON с расписанием по дням недели
    # Формат: {"monday": {"start": "09:00", "end": "18:00"}, ...}
    weekly_schedule = Column(JSON, nullable=False)
    
    # Даты начала и окончания действия расписания
    date_from = Column(DateTime, nullable=True)
    date_to = Column(DateTime, nullable=True)
    
    # Дополнительная информация
    description = Column(Text, nullable=True)
    color_code = Column(String(20), nullable=True)  # для отображения в календаре
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими таблицами
    location = relationship("Location", back_populates="schedules")
    service_schedules = relationship("ServiceSchedule", back_populates="schedule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Schedule {self.name} for {self.location.name}>"


class ServiceSchedule(Base):
    """Модель связи услуги с расписанием"""
    __tablename__ = "service_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    
    # Переопределение времени для конкретной услуги
    override_weekly_schedule = Column(JSON, nullable=True)
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими таблицами
    service = relationship("Service", back_populates="schedules")
    schedule = relationship("Schedule", back_populates="service_schedules")
    
    def __repr__(self):
        return f"<ServiceSchedule for {self.service.name}>"


class BookingStatus(str, enum.Enum):
    """Статусы бронирования"""
    PENDING = "pending"         # Ожидает подтверждения
    CONFIRMED = "confirmed"     # Подтверждено
    COMPLETED = "completed"     # Завершено
    CANCELLED = "cancelled"     # Отменено
    RESCHEDULED = "rescheduled" # Перенесено

# Класс Booking перенесен в отдельный файл app/models/booking.py
# Это предотвращает конфликт с другим определением класса Booking 
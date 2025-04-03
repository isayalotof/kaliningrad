from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from typing import List, Optional
from sqlalchemy.sql import func
import json

# Класс Location из company.py следует перенести сюда
class Location(Base):
    """Модель филиала/локации компании"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    
    # Обозначение основной локации
    is_main = Column(Boolean, default=False)
    
    # Координаты для геолокации
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Контактная информация
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    
    # Рабочие часы могут отличаться от общих для компании
    working_hours = Column(JSON, nullable=True)
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими таблицами
    company = relationship("Company", back_populates="locations")
    schedules = relationship("Schedule", back_populates="location", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Location {self.name} of {self.company.name}>" 
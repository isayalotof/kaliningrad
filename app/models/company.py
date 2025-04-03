from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from typing import List, Optional
from sqlalchemy.sql import func
import json
# Добавляем импорт модели Location
from app.models.location import Location

class Company(Base):
    """Модель компании"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    business_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Владелец компании
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Контактная информация
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    social_links = Column(Text, nullable=True)  # JSON строка
    city = Column(String(100), nullable=True)
    
    # Визуальные элементы
    logo_url = Column(String(255), nullable=True)
    cover_image_url = Column(String(255), nullable=True)
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Добавляем поле для хранения метаданных (в том числе рабочих часов)
    company_metadata = Column(Text, nullable=True)  # JSON строка
    
    # Связи с другими таблицами
    locations = relationship("Location", back_populates="company", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="company", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="company", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="company", cascade="all, delete-orphan")
    staff = relationship("CompanyStaff", back_populates="company", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="companies", foreign_keys=[owner_id])
    working_hours = relationship("WorkingHours", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company {self.name}>"

    def to_dict(self):
        """Преобразование объекта в словарь"""
        metadata_dict = {}
        if self.company_metadata:
            try:
                metadata_dict = json.loads(self.company_metadata)
            except:
                pass
                
        social_links_dict = {}
        if self.social_links:
            try:
                social_links_dict = json.loads(self.social_links)
            except:
                pass
                
        return {
            "id": self.id,
            "name": self.name,
            "business_type": self.business_type,
            "description": self.description,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "website": self.website,
            "logo_url": self.logo_url,
            "social_links": social_links_dict,
            "city": self.city,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "company_metadata": metadata_dict
        } 
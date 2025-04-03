from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"             # Администратор системы
    COMPANY_OWNER = "owner"     # Владелец компании
    MANAGER = "manager"         # Менеджер
    EMPLOYEE = "employee"       # Сотрудник


class User(Base):
    """Модель пользователя системы (сотрудники компаний)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Персональная информация
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Роль и права доступа
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Telegram интеграция
    telegram_id = Column(String(50), nullable=True)
    
    # Настройки пользователя
    settings = Column(JSON, nullable=True)
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Связи с другими таблицами
    company = relationship("Company", backref="users")
    companies = relationship("Company", back_populates="owner", foreign_keys="Company.owner_id")
    company_staff = relationship("CompanyStaff", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Client(Base):
    """Модель клиента (пользователя услуг)"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)  # Email может быть необязательным
    
    # Персональная информация
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)  # Фамилия может быть необязательной
    phone = Column(String(20), nullable=False, index=True)  # Телефон обязателен для связи
    
    # Telegram интеграция
    telegram_id = Column(String(50), nullable=True, index=True)
    
    # Настройки и предпочтения клиента
    preferences = Column(JSON, nullable=True)
    
    # Информация о клиенте для компаний
    notes = Column(Text, nullable=True)
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими таблицами
    bookings = relationship("Booking", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client {self.phone}>" 
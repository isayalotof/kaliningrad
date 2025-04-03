from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class PageView(Base):
    """
    Модель для учета просмотров страниц компании
    """
    __tablename__ = "page_views"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    page = Column(String, nullable=False)  # Страница, которую просматривали
    referrer = Column(String, nullable=True)  # Источник перехода
    ip_address = Column(String, nullable=True)  # IP-адрес пользователя
    user_agent = Column(String, nullable=True)  # User-Agent браузера
    duration = Column(Integer, nullable=True)  # Длительность просмотра в секундах
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    exit_time = Column(DateTime(timezone=True), nullable=True)  # Время выхода со страницы
    
    # Связи
    company = relationship("Company", backref="page_views")
    user = relationship("User", backref="page_views")
    
    def __repr__(self):
        return f"<PageView(id={self.id}, company_id={self.company_id}, page={self.page})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "page": self.page,
            "referrer": self.referrer,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None
        }

class UserAction(Base):
    """
    Модель для учета действий пользователей на страницах компании
    """
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String, nullable=False)  # Тип действия (клик, отправка формы и т.д.)
    action_data = Column(Text, nullable=True)  # Дополнительные данные о действии в JSON формате
    page = Column(String, nullable=False)  # Страница, на которой выполнено действие
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    company = relationship("Company", backref="user_actions")
    user = relationship("User", backref="user_actions")
    
    def __repr__(self):
        return f"<UserAction(id={self.id}, company_id={self.company_id}, action_type={self.action_type})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "action_data": self.action_data,
            "page": self.page,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SourceTracking(Base):
    """
    Модель для отслеживания источников трафика
    """
    __tablename__ = "source_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    source = Column(String, nullable=False)  # Источник (google, yandex, vk, telegram и т.д.)
    medium = Column(String, nullable=True)  # Тип источника (organic, cpc, email и т.д.)
    campaign = Column(String, nullable=True)  # Название кампании
    term = Column(String, nullable=True)  # Ключевое слово
    content = Column(String, nullable=True)  # Тип контента
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    company = relationship("Company", backref="source_tracking")
    
    def __repr__(self):
        return f"<SourceTracking(id={self.id}, company_id={self.company_id}, source={self.source})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "source": self.source,
            "medium": self.medium,
            "campaign": self.campaign,
            "term": self.term,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 
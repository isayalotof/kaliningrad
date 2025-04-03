from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Media(Base):
    """Модель для хранения медиа-файлов компаний (фото, видео и т.д.)"""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, default="photo")  # photo, video, document, etc.
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Даты создания и обновления
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Связи с другими таблицами
    company = relationship("Company", back_populates="media")
    
    def __repr__(self):
        return f"<Media {self.id}: {self.title or self.url}>" 
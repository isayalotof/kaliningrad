from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Review(Base):
    """
    Модель отзывов о компании
    """
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_name = Column(String, nullable=False)  # Имя пользователя, оставившего отзыв
    rating = Column(Float, nullable=False)  # Рейтинг от 1 до 5
    text = Column(Text, nullable=True)  # Текст отзыва
    reply = Column(Text, nullable=True)  # Ответ на отзыв от компании
    reply_date = Column(DateTime(timezone=True), nullable=True)  # Дата ответа
    is_published = Column(Boolean, default=True)  # Опубликован ли отзыв
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    company = relationship("Company", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, company_id={self.company_id}, user_name={self.user_name}, rating={self.rating})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "rating": self.rating,
            "text": self.text,
            "reply": self.reply,
            "reply_date": self.reply_date.isoformat() if self.reply_date else None,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 
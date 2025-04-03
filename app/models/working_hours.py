from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class WorkingHours(Base):
    """
    Модель рабочих часов компании
    """
    __tablename__ = "working_hours"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String, nullable=False)  # monday, tuesday, wednesday, thursday, friday, saturday, sunday
    is_working_day = Column(Boolean, default=True)
    open_time = Column(String)  # Формат HH:MM
    close_time = Column(String)  # Формат HH:MM
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь с компанией
    company = relationship("Company", back_populates="working_hours")
    
    def __repr__(self):
        return f"<WorkingHours(id={self.id}, company_id={self.company_id}, day={self.day_of_week}, open={self.open_time}, close={self.close_time})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "day_of_week": self.day_of_week,
            "is_working_day": self.is_working_day,
            "open_time": self.open_time,
            "close_time": self.close_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 
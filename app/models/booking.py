from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class Booking(Base):
    """
    Модель бронирования услуг компании
    """
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    staff_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    client_email = Column(String, nullable=True)
    
    booking_datetime = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, nullable=False)  # Длительность в минутах
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    
    price = Column(Float, nullable=True)  # Цена услуги
    prepayment = Column(Float, nullable=True)  # Предоплата
    
    status = Column(String, nullable=False, default="pending")  # pending, confirmed, completed, cancelled
    notes = Column(Text, nullable=True)  # Дополнительные заметки
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    company = relationship("Company", backref="bookings")
    service = relationship("Service", backref="bookings", foreign_keys=[service_id])
    user = relationship("User", backref="client_bookings", foreign_keys=[user_id])
    staff = relationship("User", backref="staff_bookings", foreign_keys=[staff_id])
    
    def __repr__(self):
        return f"<Booking(id={self.id}, company_id={self.company_id}, service_id={self.service_id}, status={self.status})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "service_id": self.service_id,
            "user_id": self.user_id,
            "staff_id": self.staff_id,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_email": self.client_email,
            "booking_datetime": self.booking_datetime.isoformat() if self.booking_datetime else None,
            "duration": self.duration,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "price": self.price,
            "prepayment": self.prepayment,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 
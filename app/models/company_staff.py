from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class CompanyStaff(Base):
    """
    Модель для персонала компании
    """
    __tablename__ = "company_staff"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="staff")  # admin, manager, staff
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    company = relationship("Company", back_populates="staff")
    user = relationship("User", back_populates="company_staff")
    
    def __repr__(self):
        return f"<CompanyStaff(id={self.id}, company_id={self.company_id}, user_id={self.user_id}, role={self.role})>"
    
    def to_dict(self):
        """
        Преобразование объекта в словарь
        """
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 
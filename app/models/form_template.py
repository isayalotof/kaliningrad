from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class FormTemplate(Base):
    """
    Модель для хранения шаблонов форм для разных типов бизнеса
    """
    __tablename__ = "form_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    business_type = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    fields = Column(JSON, nullable=False)  # JSON со списком полей и их типами
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FormTemplate id={self.id}, business_type={self.business_type}>"
    
    def to_dict(self):
        """
        Преобразование модели в словарь
        """
        return {
            "id": self.id,
            "business_type": self.business_type,
            "name": self.name,
            "description": self.description,
            "fields": self.fields,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 
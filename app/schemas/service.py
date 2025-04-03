from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(0.0, ge=0)
    duration: int = Field(60, ge=5)
    is_active: bool = True
    category: Optional[str] = None
    tags: Optional[str] = None

class ServiceCreate(ServiceBase):
    company_id: int

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=5)
    is_active: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[str] = None

class ServiceResponse(ServiceBase):
    id: int
    company_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class ServiceListResponse(BaseModel):
    items: List[ServiceResponse]
    total: int
    page: int
    size: int 
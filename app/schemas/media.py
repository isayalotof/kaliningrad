from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MediaBase(BaseModel):
    type: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class MediaCreate(MediaBase):
    company_id: int

class MediaUpdate(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class MediaResponse(MediaBase):
    id: int
    company_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class MediaListResponse(BaseModel):
    items: List[MediaResponse]
    total: int
    page: int
    size: int 
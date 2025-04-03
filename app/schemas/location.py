from typing import Optional
from pydantic import BaseModel

class LocationBase(BaseModel):
    city: str
    street: str
    building: str
    floor: Optional[str] = None
    office: Optional[str] = None
    additional_info: Optional[str] = None

class LocationCreate(LocationBase):
    company_id: str

class LocationResponse(LocationBase):
    id: str
    company_id: str

    class Config:
        from_attributes = True 
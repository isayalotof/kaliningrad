from pydantic import BaseModel, Field, EmailStr, validator, HttpUrl
from typing import Optional, Dict, List, Any
from datetime import datetime

# Базовые схемы для локаций

class LocationBase(BaseModel):
    """Базовая схема для локации"""
    name: str = Field(..., min_length=1, max_length=255, description="Название локации")
    address: str = Field(..., min_length=5, max_length=255, description="Адрес локации")
    city: str = Field(..., min_length=2, max_length=100, description="Город")
    postal_code: Optional[str] = Field(None, max_length=20, description="Почтовый индекс")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Контактный телефон")
    contact_email: Optional[EmailStr] = Field(None, description="Контактный email")
    working_hours: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Рабочие часы")
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")


class LocationCreate(BaseModel):
    """Схема для создания локации"""
    company_id: int = Field(..., description="ID компании")
    city: Optional[str] = Field(None, max_length=100, description="Город")
    street: Optional[str] = Field(None, max_length=255, description="Улица")
    building: Optional[str] = Field(None, max_length=50, description="Номер дома/строения")
    floor: Optional[str] = Field(None, max_length=10, description="Этаж")
    office: Optional[str] = Field(None, max_length=50, description="Номер офиса/помещения")
    additional_info: Optional[str] = Field(None, description="Дополнительная информация")
    
    class Config:
        from_attributes = True


class LocationUpdate(LocationBase):
    """Схема для обновления локации"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название локации")
    address: Optional[str] = Field(None, min_length=5, max_length=255, description="Адрес локации")
    city: Optional[str] = Field(None, min_length=2, max_length=100, description="Город")
    is_active: Optional[bool] = Field(None, description="Активна ли локация")


class LocationResponse(LocationBase):
    """Схема для ответа с локацией"""
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Базовые схемы для компаний

class CompanyBase(BaseModel):
    """Базовая схема для компании"""
    name: str = Field(..., min_length=1, max_length=255, description="Название компании")
    description: Optional[str] = Field(None, description="Описание компании")
    business_type: str = Field(..., min_length=1, max_length=50, description="Тип бизнеса")
    logo_url: Optional[HttpUrl] = Field(None, description="URL логотипа компании")
    contact_email: EmailStr = Field(..., description="Контактный email")
    contact_phone: str = Field(..., min_length=5, max_length=20, description="Контактный телефон")
    website: Optional[str] = Field(None, description="Веб-сайт компании")
    working_hours: Optional[Dict[str, Dict[str, str]]] = Field({}, description="Рабочие часы")
    special_conditions: Optional[Dict[str, Any]] = Field(None, description="Особые условия")
    brand_primary_color: Optional[str] = Field(None, max_length=20, description="Основной цвет бренда")
    brand_secondary_color: Optional[str] = Field(None, max_length=20, description="Вторичный цвет бренда")
    brand_font: Optional[str] = Field(None, max_length=50, description="Шрифт бренда")

    @validator('website', pre=True)
    def validate_website(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str) and v.startswith('http'):
            return v
        raise ValueError('Неверный формат URL. Должен начинаться с http:// или https://')


class CompanyCreate(BaseModel):
    """Схема для создания компании"""
    name: str = Field(..., min_length=1, max_length=255, description="Название компании")
    description: Optional[str] = Field(None, description="Описание компании")
    business_type: str = Field(..., min_length=1, max_length=50, description="Тип бизнеса")
    logo: Optional[str] = Field(None, description="Путь к файлу логотипа")
    email: Optional[str] = Field(None, description="Контактный email")
    phone: Optional[str] = Field(None, description="Контактный телефон")
    website: Optional[str] = Field(None, description="Веб-сайт компании")
    working_hours: Optional[str] = Field(None, description="Рабочие часы в формате JSON строки")
    is_active: Optional[bool] = Field(True, description="Активна ли компания")

    class Config:
        from_attributes = True


class CompanyUpdate(CompanyBase):
    """Схема для обновления компании"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название компании")
    business_type: Optional[str] = Field(None, min_length=1, max_length=50, description="Тип бизнеса")
    contact_email: Optional[EmailStr] = Field(None, description="Контактный email")
    contact_phone: Optional[str] = Field(None, min_length=5, max_length=20, description="Контактный телефон")
    working_hours: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Рабочие часы")
    is_active: Optional[bool] = Field(None, description="Активна ли компания")


class CompanyResponse(CompanyBase):
    """Схема для ответа с компанией"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    locations: List[LocationResponse] = []

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Ответ для списка компаний с пагинацией"""
    items: List[CompanyResponse]
    total: int
    page: int
    size: int 
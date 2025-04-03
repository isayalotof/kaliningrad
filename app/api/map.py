from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.company import CompanyService
from app.utils.business_types import get_business_type_name

router = APIRouter(prefix="/api/map", tags=["map"])

@router.get("/locations")
def get_locations(
    db: Session = Depends(get_db),
    city: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Получение списка компаний для отображения на карте
    """
    company_service = CompanyService(db)
    
    # Получаем компании с применением фильтров
    companies = company_service.get_companies_with_filter(
        city=city,
        business_type=type,
        search_query=search,
        skip=skip,
        limit=limit
    )
    
    # Формируем ответ
    locations = []
    for company in companies:
        # Получаем местоположение компании
        location = company_service.get_company_location(company.id)
        
        # Если у компании нет местоположения, пропускаем
        if not location or not location.latitude or not location.longitude:
            continue
        
        # Получаем рабочие часы
        working_hours = company_service.get_company_working_hours(company.id)
        
        # Формируем объект для ответа
        location_data = {
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "business_type": company.business_type,
            "business_type_display": get_business_type_name(company.business_type),
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "address": f"{location.city}, {location.street} {location.building}",
            "logo": company.logo if company.logo else None,
            "phone": company.phone,
            "email": company.email,
            "website": company.website,
            "rating": company.rating,
            "working_hours": working_hours
        }
        
        locations.append(location_data)
    
    return locations

@router.get("/business-types")
def get_business_types(db: Session = Depends(get_db)):
    """
    Получение списка типов бизнеса
    """
    company_service = CompanyService(db)
    types = company_service.get_business_types()
    
    # Преобразуем коды типов бизнеса в удобный для пользователя формат
    result = []
    for type_code in types:
        result.append({
            "value": type_code,
            "label": get_business_type_name(type_code)
        })
    
    return result

@router.get("/cities")
def get_cities(db: Session = Depends(get_db)):
    """
    Получение списка городов
    """
    company_service = CompanyService(db)
    cities = company_service.get_cities()
    
    # Формируем ответ
    result = []
    for city in cities:
        result.append({
            "value": city,
            "label": city
        })
    
    return result 
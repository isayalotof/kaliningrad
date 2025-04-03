from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.company import Company, Location
from app.models.user import User
from app.services.company import CompanyService
from app.schemas.company import (
    CompanyCreate, 
    CompanyUpdate, 
    CompanyResponse, 
    LocationCreate, 
    LocationUpdate, 
    LocationResponse,
    CompanyListResponse
)
from app.services.auth import get_current_user, get_current_active_user

router = APIRouter(prefix="/api/companies", tags=["companies"])

# Получение списка компаний
@router.get("/", response_model=CompanyListResponse)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получение списка компаний с пагинацией
    """
    company_service = CompanyService(db)
    companies = company_service.get_companies(skip=skip, limit=limit)
    total = company_service.count_companies()
    
    return CompanyListResponse(
        items=[CompanyResponse.model_validate(company) for company in companies],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

# Создание новой компании
@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate, 
    db: Session = Depends(get_db)
):
    """Создать новую компанию"""
    service = CompanyService(db)
    company = service.create_company(company_data)
    return company

# Получение информации о компании
@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int = Path(..., title="ID компании"),
    db: Session = Depends(get_db)
):
    """
    Получение информации о компании по ID
    """
    company_service = CompanyService(db)
    company = company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    return CompanyResponse.model_validate(company)

# Обновление информации о компании
@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_data: CompanyUpdate,
    company_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Обновить информацию о компании"""
    service = CompanyService(db)
    company = service.update_company(company_id, company_data)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    return company

# Удаление компании
@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Удалить компанию"""
    service = CompanyService(db)
    success = service.delete_company(company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    return {"detail": "Компания успешно удалена"}

# Работа с локациями

# Получение списка локаций компании
@router.get("/{company_id}/locations", response_model=List[LocationResponse])
async def get_company_locations(
    company_id: int = Path(..., title="ID компании"),
    db: Session = Depends(get_db)
):
    """
    Получение списка локаций компании
    """
    company_service = CompanyService(db)
    company = company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    locations = company_service.get_company_locations(company_id)
    return locations

# Создание новой локации
@router.post("/{company_id}/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    company_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Создать новую локацию для компании"""
    service = CompanyService(db)
    location = service.create_location(company_id, location_data)
    return location

@router.get("/{company_id}/services")
async def get_company_services(
    company_id: int = Path(..., title="ID компании"),
    db: Session = Depends(get_db)
):
    """
    Получение списка услуг компании
    """
    company_service = CompanyService(db)
    company = company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    services = company_service.get_company_services(company_id)
    return services

@router.get("/{company_id}/media")
async def get_company_media(
    company_id: int = Path(..., title="ID компании"),
    db: Session = Depends(get_db)
):
    """
    Получение списка медиа-файлов компании
    """
    company_service = CompanyService(db)
    company = company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    media = company_service.get_company_media(company_id)
    return media 
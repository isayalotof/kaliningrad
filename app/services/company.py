from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import or_
import json

from app.models.company import Company, Location
from app.models.service import Service
from app.models.media import Media
from app.schemas.company import CompanyCreate, CompanyUpdate, LocationCreate, LocationUpdate
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.media import MediaCreate, MediaUpdate
from app.models.working_hours import WorkingHours
from app.models.review import Review
from app.models.company_staff import CompanyStaff

class CompanyService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """
        Получить список компаний с пагинацией
        """
        return self.db.query(Company).offset(skip).limit(limit).all()
    
    def count_companies(self) -> int:
        """
        Получить общее количество компаний в базе данных
        """
        return self.db.query(Company).count()
    
    def get_company(self, company_id: int) -> Optional[Company]:
        """
        Получить компанию по ID
        """
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def create_company(self, company_data: CompanyCreate) -> Company:
        """
        Создать новую компанию
        """
        # Преобразование данных Pydantic в dict для создания модели
        company_dict = company_data.model_dump()
        
        # Создание объекта модели
        db_company = Company(**company_dict)
        
        # Сохранение в базе данных
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        
        return db_company
    
    def update_company(self, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
        """
        Обновить информацию о компании
        """
        # Получение компании из БД
        db_company = self.get_company(company_id)
        if not db_company:
            return None
        
        # Обновление только переданных полей
        company_data_dict = company_data.model_dump(exclude_unset=True)
        
        # Обновление полей модели
        for key, value in company_data_dict.items():
            setattr(db_company, key, value)
        
        # Обновление времени изменения
        db_company.updated_at = datetime.utcnow()
        
        # Сохранение изменений
        self.db.commit()
        self.db.refresh(db_company)
        
        return db_company
    
    def delete_company(self, company_id: int) -> bool:
        """
        Удалить компанию
        """
        db_company = self.get_company(company_id)
        if not db_company:
            return False
        
        # Удаление из БД
        self.db.delete(db_company)
        self.db.commit()
        
        return True
    
    # Методы для работы с локациями
    
    def get_company_locations(self, company_id: int) -> List[Location]:
        """
        Получить список локаций компании
        """
        return self.db.query(Location).filter(Location.company_id == company_id).all()
    
    def get_location(self, location_id: int) -> Optional[Location]:
        """
        Получить локацию по ID
        """
        return self.db.query(Location).filter(Location.id == location_id).first()
    
    def create_location(self, company_id: int, location_data: LocationCreate) -> Location:
        """
        Создать новую локацию для компании
        """
        # Проверка существования компании
        company = self.get_company(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Компания с ID {company_id} не найдена"
            )
        
        # Преобразование данных Pydantic в dict для создания модели
        location_dict = location_data.model_dump()
        
        # Добавление ID компании
        location_dict["company_id"] = company_id
        
        # Создание объекта модели
        db_location = Location(**location_dict)
        
        # Сохранение в базе данных
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        
        return db_location
    
    def update_location(self, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
        """
        Обновить информацию о локации
        """
        # Получение локации из БД
        db_location = self.get_location(location_id)
        if not db_location:
            return None
        
        # Обновление только переданных полей
        location_data_dict = location_data.model_dump(exclude_unset=True)
        
        # Обновление полей модели
        for key, value in location_data_dict.items():
            setattr(db_location, key, value)
        
        # Обновление времени изменения
        db_location.updated_at = datetime.utcnow()
        
        # Сохранение изменений
        self.db.commit()
        self.db.refresh(db_location)
        
        return db_location
    
    def delete_location(self, location_id: int) -> bool:
        """
        Удалить локацию
        """
        db_location = self.get_location(location_id)
        if not db_location:
            return False
        
        # Удаление из БД
        self.db.delete(db_location)
        self.db.commit()
        
        return True
    
    # Методы для работы с услугами
    def get_company_services(self, company_id: int) -> List:
        """
        Получение списка услуг компании
        """
        services = self.db.query(Service).filter(Service.company_id == company_id).all()
        return services
    
    def get_service(self, service_id: int) -> Optional[Service]:
        """
        Получить услугу по ID
        """
        return self.db.query(Service).filter(Service.id == service_id).first()
    
    def create_service(self, company_id: int, service_data: Dict[str, Any]) -> Service:
        """
        Создать новую услугу для компании
        """
        # Проверка существования компании
        company = self.get_company(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Компания с ID {company_id} не найдена"
            )
        
        # Создание объекта услуги
        db_service = Service(
            company_id=company_id,
            name=service_data.get("name", ""),
            description=service_data.get("description", ""),
            price=service_data.get("price", 0.0),
            duration=service_data.get("duration", 60),
            is_active=service_data.get("is_active", True)
        )
        
        # Сохранение в базе данных
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        
        return db_service
    
    def update_service(self, service_id: int, service_data: Dict[str, Any]) -> Optional[Service]:
        """
        Обновить информацию об услуге
        """
        # Получение услуги из БД
        db_service = self.get_service(service_id)
        if not db_service:
            return None
        
        # Обновление полей модели
        for key, value in service_data.items():
            setattr(db_service, key, value)
        
        # Обновление времени изменения
        db_service.updated_at = datetime.utcnow()
        
        # Сохранение изменений
        self.db.commit()
        self.db.refresh(db_service)
        
        return db_service
    
    def delete_service(self, service_id: int) -> bool:
        """
        Удалить услугу
        """
        db_service = self.get_service(service_id)
        if not db_service:
            return False
        
        # Удаление из БД
        self.db.delete(db_service)
        self.db.commit()
        
        return True
    
    # Методы для работы с медиа-файлами
    def get_company_media(self, company_id: int) -> List:
        """
        Получение медиа-файлов компании
        """
        media = self.db.query(Media).filter(Media.company_id == company_id).all()
        return media
    
    def get_media(self, media_id: int) -> Optional[Media]:
        """
        Получить медиа-файл по ID
        """
        return self.db.query(Media).filter(Media.id == media_id).first()
    
    def create_media(self, company_id: int, media_data: Dict[str, Any]) -> Media:
        """
        Создать новый медиа-файл для компании
        """
        # Проверка существования компании
        company = self.get_company(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Компания с ID {company_id} не найдена"
            )
        
        # Создание объекта медиа
        db_media = Media(
            company_id=company_id,
            type=media_data.get("type", "photo"),
            url=media_data.get("url", ""),
            title=media_data.get("title", ""),
            description=media_data.get("description", ""),
            sort_order=media_data.get("sort_order", 0),
            is_active=media_data.get("is_active", True)
        )
        
        # Сохранение в базе данных
        self.db.add(db_media)
        self.db.commit()
        self.db.refresh(db_media)
        
        return db_media
    
    def update_media(self, media_id: int, media_data: Dict[str, Any]) -> Optional[Media]:
        """
        Обновить информацию о медиа-файле
        """
        # Получение медиа из БД
        db_media = self.get_media(media_id)
        if not db_media:
            return None
        
        # Обновление полей модели
        for key, value in media_data.items():
            setattr(db_media, key, value)
        
        # Обновление времени изменения
        db_media.updated_at = datetime.utcnow()
        
        # Сохранение изменений
        self.db.commit()
        self.db.refresh(db_media)
        
        return db_media
    
    def delete_media(self, media_id: int) -> bool:
        """
        Удалить медиа-файл
        """
        db_media = self.get_media(media_id)
        if not db_media:
            return False
        
        # Удаление из БД
        self.db.delete(db_media)
        self.db.commit()
        
        return True
    
    def get_company_working_hours(self, company_id: int) -> Dict:
        """
        Получение рабочих часов компании
        """
        working_hours = self.db.query(WorkingHours).filter(WorkingHours.company_id == company_id).all()
        
        if not working_hours:
            # Пробуем получить рабочие часы из метаданных компании
            company = self.get_company(company_id)
            if company and company.company_metadata:
                try:
                    metadata = json.loads(company.company_metadata)
                    if isinstance(metadata, dict) and 'working_hours' in metadata:
                        return metadata['working_hours']
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Ошибка при получении рабочих часов из метаданных: {str(e)}")
            return {}
        
        result = {}
        for day in working_hours:
            result[day.day_of_week] = {
                "is_working_day": day.is_working_day,
                "open_time": day.open_time,
                "close_time": day.close_time
            }
        
        return result

    def get_company_reviews(self, company_id: int) -> List:
        """
        Получение отзывов о компании
        """
        reviews = self.db.query(Review).filter(Review.company_id == company_id).all()
        return reviews

    def get_business_types(self) -> List[str]:
        """
        Получение списка типов бизнеса
        """
        types = self.db.query(Company.business_type).distinct().all()
        return [type[0] for type in types if type[0]]

    def get_cities(self) -> List[str]:
        """
        Получение списка городов
        """
        cities = self.db.query(Location.city).distinct().all()
        return [city[0] for city in cities if city[0]]

    def get_companies_with_filter(
        self, 
        city: Optional[str] = None, 
        business_type: Optional[str] = None, 
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Company]:
        """
        Получение списка компаний с фильтрацией
        """
        query = self.db.query(Company).join(Location, Location.company_id == Company.id, isouter=True)
        
        # Фильтрация по городу
        if city:
            query = query.filter(Location.city == city)
        
        # Фильтрация по типу бизнеса
        if business_type:
            query = query.filter(Company.business_type == business_type)
        
        # Фильтрация по поисковому запросу
        if search_query:
            query = query.filter(
                or_(
                    Company.name.ilike(f"%{search_query}%"),
                    Company.description.ilike(f"%{search_query}%")
                )
            )
        
        # Добавляем фильтр по активным компаниям
        query = query.filter(Company.is_active == True)
        
        # Применяем пагинацию
        query = query.offset(skip).limit(limit)
        
        return query.all()

    def check_user_has_access(self, user_id: int, company_id: int) -> bool:
        """
        Проверка доступа пользователя к компании
        """
        # Проверяем, является ли пользователь владельцем компании
        company = self.get_company(company_id)
        if not company:
            return False
        
        if company.owner_id == user_id:
            return True
        
        # Проверяем, есть ли у пользователя роль сотрудника в компании
        staff = self.db.query(CompanyStaff).filter(
            CompanyStaff.company_id == company_id,
            CompanyStaff.user_id == user_id,
            CompanyStaff.is_active == True
        ).first()
        
        return staff is not None

    def get_company_location(self, company_id: int) -> Optional[Location]:
        """
        Получение основной локации компании
        """
        return self.db.query(Location).filter(
            Location.company_id == company_id,
            Location.is_main == True
        ).first() or self.db.query(Location).filter(
            Location.company_id == company_id
        ).first() 
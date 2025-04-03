from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Query, Path, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import uuid
import os
import logging
from pydantic import ValidationError
from datetime import datetime, timedelta
import re

from app.core.database import get_db
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyBase
from app.schemas.location import LocationCreate
from app.services.company import CompanyService
from app.utils.file_utils import save_uploaded_file
from app.services.auth import get_current_user
from app.utils.auth_utils import get_current_user_optional
from app.services.analytics import AnalyticsService
from app.models.company import Company
from app.models.location import Location
from app.models.user import User
from app.models.service import Service
from app.models.media import Media
from app.models.working_hours import WorkingHours
from app.services.form_template import FormTemplateService

# Настройка логгера
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Используем класс Pydantic вместо модели для валидации данных рабочих часов
from pydantic import BaseModel

class WorkingHoursModel(BaseModel):
    company_id: int
    day: str
    open_time: str
    close_time: str
    is_working: bool = True

# Маршрут для страницы авторизации (входа)
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Отображение страницы входа
    """
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Вход в аккаунт"}
    )

# Маршрут для страницы регистрации пользователя
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """
    Отображение страницы регистрации пользователя
    """
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "title": "Регистрация аккаунта"}
    )

# Маршрут для страницы регистрации бизнеса
@router.get("/register", response_class=HTMLResponse)
async def business_register_page(request: Request):
    """
    Отображение страницы регистрации бизнеса
    """
    return templates.TemplateResponse(
        "business_module.html", 
        {"request": request, "title": "Регистрация бизнеса"}
    )

# Маршрут для страницы аналитики бизнеса
@router.get("/analytics", response_class=HTMLResponse)
async def business_analytics_page(request: Request, current_user: Dict = Depends(get_current_user_optional)):
    """
    Отображение страницы аналитики бизнеса
    """
    # В будущем здесь будет проверка прав доступа к аналитике бизнеса
    return templates.TemplateResponse(
        "business_analytics.html", 
        {
            "request": request, 
            "title": "Аналитика бизнеса",
            "current_user": current_user,
            "now": datetime.now()
        }
    )

# Маршрут для личного кабинета бизнеса
@router.get("/dashboard", response_class=HTMLResponse)
async def business_dashboard_page(request: Request, current_user: Dict = Depends(get_current_user_optional)):
    """
    Отображение личного кабинета бизнеса
    """
    # В будущем здесь будет проверка прав доступа и загрузка данных компании
    return templates.TemplateResponse(
        "business_dashboard.html", 
        {
            "request": request, 
            "title": "Личный кабинет бизнеса",
            "current_user": current_user,
            "now": datetime.now()
        }
    )

# Маршрут для редактирования профиля бизнеса
@router.get("/profile/edit/{company_id}", response_class=HTMLResponse)
async def business_profile_edit_page(
    request: Request, 
    company_id: int, 
    current_user: Dict = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Страница редактирования профиля бизнеса
    """
    # Получаем сервис для работы с компаниями
    company_service = CompanyService(db)
    
    # Получаем данные компании из БД
    company = company_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Проверяем права доступа
    if current_user is None or (company.owner_id != current_user.get("id") and 
                                not company_service.check_user_has_access(current_user.get("id"), company_id)):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Получаем локацию компании
    locations = company_service.get_company_locations(company_id)
    location = locations[0] if locations else None
    
    # Получаем рабочие часы
    working_hours = company_service.get_company_working_hours(company_id)
    
    # Получаем медиа-файлы
    media_files = company_service.get_company_media(company_id)
    
    # Формируем данные для шаблона
    company_data = {
        "id": company.id,
        "name": company.name,
        "business_type": company.business_type,
        "description": company.description,
        "phone": company.contact_phone,
        "email": company.contact_email,
        "website": company.website,
        "logo": company.logo_url,
        "gallery": [file.url for file in media_files if file.type == 'photo'] if media_files else [],
        "location": location.to_dict() if location else {},
        "working_hours": working_hours if working_hours else {
            "monday": {"is_working_day": True, "open_time": "09:00", "close_time": "18:00"},
            "tuesday": {"is_working_day": True, "open_time": "09:00", "close_time": "18:00"},
            "wednesday": {"is_working_day": True, "open_time": "09:00", "close_time": "18:00"},
            "thursday": {"is_working_day": True, "open_time": "09:00", "close_time": "18:00"},
            "friday": {"is_working_day": True, "open_time": "09:00", "close_time": "18:00"},
            "saturday": {"is_working_day": True, "open_time": "10:00", "close_time": "16:00"},
            "sunday": {"is_working_day": False, "open_time": "", "close_time": ""}
        },
        "social_networks": company.social_links or {}
    }
    
    return templates.TemplateResponse(
        "business_profile_edit.html", 
        {
            "request": request, 
            "title": f"Редактирование профиля: {company.name}",
            "current_user": current_user,
            "company": company_data,
            "now": datetime.now()
        }
    )

# Маршрут для просмотра профиля бизнеса
@router.get("/profile/{company_id}", response_class=HTMLResponse)
async def view_business_profile(request: Request, company_id: int, current_user: Dict = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    """
    Просмотр профиля бизнеса
    """
    # Получаем данные компании из БД по ID
    company_service = CompanyService(db)
    company = company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Получаем локацию компании
    locations = company_service.get_company_locations(company_id)
    location = locations[0] if locations else None
    
    # Получаем услуги компании
    services = company_service.get_company_services(company_id)
    
    # Получаем рабочие часы
    working_hours = company_service.get_company_working_hours(company_id)
    
    # Получаем отзывы
    reviews = company_service.get_company_reviews(company_id)
    
    # Получаем медиа-файлы
    media_files = company_service.get_company_media(company_id)
    
    # Формируем данные для шаблона
    company_data = {
        "id": company.id,
        "name": company.name,
        "business_type": company.business_type,
        "description": company.description,
        "phone": company.contact_phone,
        "email": company.contact_email,
        "website": company.website,
        "logo": company.logo_url,
        "rating": company.rating if hasattr(company, 'rating') else None,
        "reviews_count": len(reviews) if reviews else 0,
        "location": location.to_dict() if location else None,
        "working_hours": working_hours if working_hours else {},
        "services": [service.to_dict() for service in services] if services else [],
        "gallery": [file.url for file in media_files if file.type == 'photo'] if media_files else []
    }
    
    # Передаем данные в шаблон
    return templates.TemplateResponse(
        "business_profile.html", 
        {
            "request": request, 
            "company": company_data,
            "current_user": current_user
        }
    )

# API для получения шаблона формы в зависимости от типа бизнеса
@router.get("/form-template/{business_type}")
async def get_form_template(business_type: str, db: Session = Depends(get_db)):
    """
    Получение шаблона формы в зависимости от типа бизнеса
    """
    # Получаем сервис для работы с шаблонами форм
    template_service = FormTemplateService(db)
    
    # Пробуем получить шаблон из базы данных
    template = template_service.get_template_by_business_type(business_type)
    
    # Если шаблон не найден
    if not template:
        # Инициализируем дефолтные шаблоны
        template_service.init_default_templates()
        
        # Пробуем получить шаблон еще раз
        template = template_service.get_template_by_business_type(business_type)
        
        # Если шаблон все равно не найден, возвращаем ошибку
        if not template:
            raise HTTPException(status_code=404, detail=f"Шаблон для типа бизнеса {business_type} не найден")
    
    # Возвращаем шаблон формы
    return {
        "id": template.id,
        "business_type": template.business_type,
        "name": template.name,
        "description": template.description,
        "fields": template.fields
    }

# API для регистрации бизнеса
@router.post("/register", status_code=201)
async def register_business(
    request: Request,
    name: str = None,
    business_type: str = None,
    contact_name: str = None,
    contact_email: str = None,
    contact_phone: str = None,
    description: str = None,
    address: str = None,
    city: str = None,
    working_hours: str = None,
    services: str = None,
    social_links: str = None,
    logo: UploadFile = None,
    photos: List[UploadFile] = None,
    user: Optional[Dict] = None,
    db: Session = Depends(get_db),
    owner_id: int = None
):
    """Регистрация бизнеса"""
    logger.info("Запрос на регистрацию бизнеса.")
    logger.info(f"Данные: {name}, {business_type}")
    
    try:
        # Валидация обязательных полей
        if not name or not business_type:
            logger.error("Ошибка валидации: не указано название или тип бизнеса")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "Не указано название или тип бизнеса"}
            )
        
        # Создаем компанию
        company = Company(
            name=name,
            business_type=business_type,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            description=description,
            city=city,
            owner_id=owner_id
        )
        
        # Если переданы социальные ссылки, преобразуем их в JSON
        if social_links:
            try:
                social_links_data = json.loads(social_links)
                # Валидация формата
                if isinstance(social_links_data, dict):
                    company.social_links = social_links
            except json.JSONDecodeError:
                logger.error(f"Ошибка парсинга social_links: {social_links}")
        
        # Сохраняем файл логотипа, если он был загружен
        if logo:
            try:
                logo_path = await save_uploaded_file(logo, "logo", subfolder=f"company_{owner_id}")
                company.logo_url = logo_path
                logger.info(f"Логотип сохранен: {logo_path}")
            except Exception as e:
                logger.error(f"Ошибка сохранения логотипа: {str(e)}")
        
        # Добавляем компанию в базу данных
        db.add(company)
        db.flush()  # Получаем ID компании
        logger.info(f"Создана компания с ID: {company.id}")
        
        # Создаем локацию для компании
        if address:
            try:
                location = Location(
                    company_id=company.id,
                    name=f"{name} - Основной филиал",
                    address=address,
                    city=city or "",
                    is_main=True,
                    contact_phone=contact_phone,
                    contact_email=contact_email
                )
                db.add(location)
                db.flush()  # Получаем ID созданной локации
                logger.info(f"Создана локация с ID: {location.id}")
            except Exception as e:
                logger.error(f"Ошибка создания локации: {str(e)}")
        
        # Обрабатываем рабочие часы, если они были переданы
        saved_hours = 0
        if working_hours:
            try:
                hours_data = json.loads(working_hours)
                logger.info(f"Получены данные рабочих часов: {hours_data}")
                
                # Сохраняем рабочие часы в базу данных через модель WorkingHours
                for day, hours in hours_data.items():
                    if isinstance(hours, dict) and "from" in hours and "to" in hours:
                        # Проверяем корректность формата времени
                        time_pattern = re.compile(r'^\d{1,2}:\d{2}$')
                        if not (time_pattern.match(hours["from"]) and time_pattern.match(hours["to"])):
                            continue
                        
                        # Создаем запись о рабочих часах для этого дня
                        working_hour = WorkingHours(
                            company_id=company.id,
                            day_of_week=day,
                            is_working_day=hours.get("isWorking", True),
                            open_time=hours["from"],
                            close_time=hours["to"]
                        )
                        db.add(working_hour)
                        saved_hours += 1
                        
                # Для обратной совместимости также сохраняем в метаданные
                company_metadata = {}
                try:
                    if company.company_metadata:
                        company_metadata = json.loads(company.company_metadata)
                except:
                    company_metadata = {}
                
                # Добавляем рабочие часы в метаданные
                if not isinstance(company_metadata, dict):
                    company_metadata = {}
                    
                company_metadata["working_hours"] = {}
                
                for day, hours in hours_data.items():
                    if isinstance(hours, dict) and "from" in hours and "to" in hours:
                        company_metadata["working_hours"][day] = {
                            "open_time": hours["from"],
                            "close_time": hours["to"],
                            "is_working": hours.get("isWorking", True)
                        }
                
                # Сохраняем метаданные в компанию
                company.company_metadata = json.dumps(company_metadata)
                
                logger.info(f"Сохранено {saved_hours} записей о рабочих часах")
            except json.JSONDecodeError:
                logger.error(f"Ошибка парсинга working_hours: {working_hours}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении рабочих часов: {str(e)}")
        
        # Обрабатываем услуги, если они были переданы
        saved_services = 0
        if services:
            try:
                services_data = json.loads(services)
                logger.info(f"Получены данные услуг: {services_data}")
                
                if isinstance(services_data, list):
                    for service_data in services_data:
                        if isinstance(service_data, dict) and "name" in service_data:
                            service = Service(
                                company_id=company.id,
                                name=service_data.get("name", ""),
                                description=service_data.get("description", ""),
                                price=service_data.get("price", 0),
                                duration=service_data.get("duration", 60)
                            )
                            db.add(service)
                            saved_services += 1
                
                logger.info(f"Сохранено {saved_services} услуг")
            except json.JSONDecodeError:
                logger.error(f"Ошибка парсинга services: {services}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении услуг: {str(e)}")
        
        # Обрабатываем фотографии, если они были загружены
        saved_photos = 0
        if photos:
            for photo in photos[:5]:  # Ограничиваем до 5 фотографий
                try:
                    photo_path = await save_uploaded_file(photo, "photo", subfolder=f"company_{company.id}")
                    media = Media(
                        company_id=company.id,
                        type="image",
                        url=photo_path,
                        title=f"Photo {saved_photos+1}"
                    )
                    db.add(media)
                    saved_photos += 1
                    logger.info(f"Сохранено фото: {photo_path}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения фото: {str(e)}")
        
        # Фиксируем все изменения в базе данных
        db.commit()
        logger.info(f"Регистрация бизнеса успешно завершена. ID: {company.id}")
        
        # Возвращаем успешный ответ
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Бизнес успешно зарегистрирован",
                "company_id": company.id
            }
        )
    
    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        db.rollback()
        logger.error(f"Ошибка при регистрации бизнеса: {str(e)}")
        
        # Возвращаем ошибку
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"Произошла ошибка при регистрации бизнеса: {str(e)}"
            }
        )

# API для получения данных аналитики
@router.get("/api/company/{company_id}/analytics")
async def get_company_analytics(
    company_id: int,
    period: str = Query("month", description="Период для отображения аналитики (day, week, month, year)"),
    start_date: Optional[str] = Query(None, description="Начальная дата в формате YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Конечная дата в формате YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение аналитических данных для компании
    """
    # Создаем экземпляр сервиса компаний
    company_service = CompanyService(db)
    
    # Проверяем существование компании
    company = company_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Проверяем права доступа
    if not company_service.check_user_has_access(current_user.id, company_id):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    # Обрабатываем даты
    try:
        if start_date and end_date:
            # Используем указанные даты
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            # Используем период
            end_date_dt = datetime.now()
            if period == "day":
                start_date_dt = end_date_dt - timedelta(days=1)
            elif period == "week":
                start_date_dt = end_date_dt - timedelta(weeks=1)
            elif period == "year":
                start_date_dt = end_date_dt - timedelta(days=365)
            else:  # month (по умолчанию)
                start_date_dt = end_date_dt - timedelta(days=30)
            
            # Сбрасываем время для start_date
            start_date_dt = start_date_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Получаем аналитику
    analytics_service = AnalyticsService(db)
    analytics_data = analytics_service.get_company_analytics(company_id, start_date_dt, end_date_dt)
    
    return analytics_data

@router.post("/api/register", status_code=201)
async def register_business_api(
    request: Request,
    name: str = Form(None),
    business_type: str = Form(None),
    contact_name: str = Form(None),
    contact_email: str = Form(None),
    contact_phone: str = Form(None),
    description: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    working_hours: str = Form(None),
    services: str = Form(None),
    social_links: str = Form(None),
    logo: UploadFile = File(None),
    photos: List[UploadFile] = File([]),
    current_user: Dict = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """API для регистрации бизнеса"""
    logger.info("API запрос на регистрацию бизнеса.")
    logger.info(f"Данные: имя = {name}, тип = {business_type}")
    
    # Для тестирования: установим владельца бизнеса равным 1, если пользователь не авторизован
    owner_id = current_user.get("id") if current_user else 1
    
    return await register_business(
        request=request,
        name=name,
        business_type=business_type,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_phone=contact_phone,
        description=description,
        address=address,
        city=city,
        working_hours=working_hours,
        services=services,
        social_links=social_links,
        logo=logo,
        photos=photos,
        user=None,  # Используем owner_id вместо user
        db=db,
        owner_id=owner_id
    ) 
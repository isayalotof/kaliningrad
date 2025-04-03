from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import business_module, auth, map, company
from app.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Business Platform API",
    description="API для бизнес-платформы",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключение шаблонов
templates = Jinja2Templates(directory="app/templates")

# Подключение маршрутов API
app.include_router(business_module.router, prefix="/business")
app.include_router(auth.router)
app.include_router(map.router)
app.include_router(company.router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Qwerty.town - Бизнес-платформа"})

# Маршруты для страниц логина и регистрации перенесены в business_module.py с префиксом /business

@app.get("/business/module")
async def business_module_page(request: Request):
    return templates.TemplateResponse("business_module.html", {"request": request, "title": "Регистрация бизнеса"})

@app.get("/business/profile/{company_id}")
async def business_profile_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_profile.html", {"request": request, "company_id": company_id, "title": "Профиль компании"})

@app.get("/business/dashboard/{company_id}")
async def business_dashboard_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_dashboard.html", {"request": request, "company_id": company_id, "title": "Панель управления"})

@app.get("/business/analytics/{company_id}")
async def business_analytics_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_analytics.html", {"request": request, "company_id": company_id, "title": "Аналитика"})

@app.get("/business/profile-edit/{company_id}")
async def business_profile_edit_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_profile_edit.html", {"request": request, "company_id": company_id, "title": "Редактирование профиля"})

@app.get("/business/schedule/{company_id}")
async def business_schedule_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_schedule.html", {"request": request, "company_id": company_id, "title": "Управление расписанием"})

@app.get("/business/bookings/{company_id}")
async def business_bookings_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_bookings.html", {"request": request, "company_id": company_id, "title": "Управление бронированиями"})

@app.get("/business/telegram/{company_id}")
async def business_telegram_page(request: Request, company_id: int):
    return templates.TemplateResponse("business_telegram.html", {"request": request, "company_id": company_id, "title": "Настройка Telegram"})

# Маршруты без указания ID компании - будут автоматически перенаправлять на страницу с ID текущей компании пользователя
@app.get("/business/profile")
async def business_profile_redirect_page(request: Request):
    return templates.TemplateResponse("business_profile_redirect.html", {"request": request, "title": "Перенаправление на профиль"})

@app.get("/business/dashboard")
async def business_dashboard_redirect_page(request: Request):
    return templates.TemplateResponse("business_dashboard_redirect.html", {"request": request, "title": "Перенаправление на панель управления"})

@app.get("/business/analytics")
async def business_analytics_redirect_page(request: Request):
    return templates.TemplateResponse("business_analytics_redirect.html", {"request": request, "title": "Перенаправление на аналитику"})

@app.get("/business/schedule")
async def business_schedule_redirect_page(request: Request):
    return templates.TemplateResponse("business_schedule_redirect.html", {"request": request, "title": "Перенаправление на расписание"})

@app.get("/business/bookings")
async def business_bookings_redirect_page(request: Request):
    return templates.TemplateResponse("business_bookings_redirect.html", {"request": request, "title": "Перенаправление на бронирования"})

@app.get("/business/telegram")
async def business_telegram_redirect_page(request: Request):
    return templates.TemplateResponse("business_telegram_redirect.html", {"request": request, "title": "Перенаправление на настройки Telegram"})

@app.get("/map")
async def map_page(request: Request):
    return templates.TemplateResponse("map.html", {"request": request, "title": "Карта компаний"})

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

# Инициализация базовых данных
@app.on_event("startup")
async def initialize_data():
    """Инициализирует базовые данные при запуске приложения"""
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    from app.services.form_template import FormTemplateService
    
    # Создаем сессию базы данных
    db = SessionLocal()
    try:
        # Инициализируем шаблоны форм
        template_service = FormTemplateService(db)
        template_service.init_default_templates()
        
        # Здесь можно добавить инициализацию других базовых данных
        
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
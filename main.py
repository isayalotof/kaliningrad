from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Создание экземпляра FastAPI
app = FastAPI(
    title="Qwerty.town - Бизнес-модуль",
    description="Веб-модуль для юридических лиц, управляющий бизнес-процессами",
    version="0.1.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="app/templates")

# Импорт маршрутов из модулей API
from app.api.company import router as company_router
# from app.api.schedule import router as schedule_router
# from app.api.booking import router as booking_router
# from app.api.analytics import router as analytics_router
# from app.api.telegram import router as telegram_router
from app.api.business_module import router as business_module_router

# Регистрация маршрутов
app.include_router(company_router, prefix="/api/company", tags=["company"])
# app.include_router(schedule_router, prefix="/api/schedule", tags=["schedule"])
# app.include_router(booking_router, prefix="/api/booking", tags=["booking"])
# app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
# app.include_router(telegram_router, prefix="/api/telegram", tags=["telegram"])
app.include_router(business_module_router, prefix="/business", tags=["business"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Главная страница
    """
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Qwerty.town - Бизнес-модуль"}
    )

# Обработчик статуса
@app.get("/status")
async def status():
    """
    Эндпоинт для проверки статуса сервера
    """
    return {"status": "ok", "version": "0.1.0"}

# Обработчик ошибок 404
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """
    Обработчик ошибок 404
    """
    return templates.TemplateResponse(
        "404.html", 
        {"request": request, "title": "Страница не найдена"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port,
        reload=True
    ) 
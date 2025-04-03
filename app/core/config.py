import os
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from functools import lru_cache

class Settings(BaseModel):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "Qwerty.town"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "очень_секретный_ключ_замените_в_продакшене")
    
    # База данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/qwertytown"
    )
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", SECRET_KEY)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", None)
    TELEGRAM_WEBHOOK_URL: Optional[str] = os.getenv("TELEGRAM_WEBHOOK_URL", None)
    
    # RabbitMQ
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    # Cors
    CORS_ORIGINS: List[str] = ["*"]  # В продакшене заменить на конкретные домены
    
    # Шаблоны
    TEMPLATES_DIR: str = "app/templates"
    
    # Статические файлы
    STATIC_DIR: str = "app/static"
    
    # Яндекс.Карты API
    YANDEX_MAPS_API_KEY: Optional[str] = os.getenv("YANDEX_MAPS_API_KEY", None)
    
    # Битрикс24 API
    BITRIX24_WEBHOOK_URL: Optional[str] = os.getenv("BITRIX24_WEBHOOK_URL", None)
    
    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Получение настроек с кэшированием"""
    return Settings()


settings = get_settings() 
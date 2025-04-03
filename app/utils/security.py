from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Создание контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка соответствия пароля хешу
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Получение хеша пароля
    """
    return pwd_context.hash(password)

def is_secure_password(password: str) -> bool:
    """
    Проверка надежности пароля
    
    Условия:
    - Минимум 8 символов
    - Содержит хотя бы одну цифру
    - Содержит хотя бы одну букву в верхнем регистре
    - Содержит хотя бы одну букву в нижнем регистре
    - Содержит хотя бы один специальный символ
    """
    if len(password) < 8:
        return False
    
    has_digit = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    special_chars = "!@#$%^&*()_-+={}[]\\|:;\"'<>,.?/"
    has_special = any(char in special_chars for char in password)
    
    # Базовая проверка - минимум 3 из 4 условий
    conditions_met = sum([has_digit, has_upper, has_lower, has_special])
    return conditions_met >= 3

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None, 
                        extra_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Создание JWT токена
    
    Args:
        subject: Идентификатор пользователя (обычно ID или email)
        expires_delta: Время жизни токена
        extra_data: Дополнительные данные для включения в токен
        
    Returns:
        Строка с JWT токеном
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Базовые данные токена
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Добавление дополнительных данных
    if extra_data:
        to_encode.update(extra_data)
    
    # Кодирование токена
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирование JWT токена
    
    Args:
        token: JWT токен
        
    Returns:
        Словарь с данными из токена
        
    Raises:
        JWTError: Если токен невалидный
    """
    return jwt.decode(
        token, 
        settings.JWT_SECRET, 
        algorithms=[settings.JWT_ALGORITHM]
    ) 
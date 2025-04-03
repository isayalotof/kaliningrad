from typing import Dict, Optional, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирование JWT токена
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return {}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """
    Получение текущего пользователя по JWT токену
    """
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id: int = payload.get("sub")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

async def get_current_user_optional(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[Dict]:
    """
    Получение текущего пользователя (необязательно)
    """
    user = await get_current_user(token, db)
    if not user:
        return None
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }

async def get_current_user_required(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Получение текущего пользователя (обязательно)
    """
    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user 
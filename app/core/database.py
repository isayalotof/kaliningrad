from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создание движка SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    """
    Зависимость для получения сессии БД с автоматическим закрытием
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
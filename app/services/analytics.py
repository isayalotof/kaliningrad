"""
Сервис для работы с аналитическими данными бизнеса
"""

from datetime import datetime, timedelta
import random
import logging
from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func, distinct, and_, or_, desc

from app.services.company import CompanyService
from app.models.company import Company
from app.models.booking import Booking
from app.models.service import Service
from app.models.stats import PageView, UserAction
from app.models.analytics import SourceTracking

# Настройка логгера
logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Сервис для получения аналитических данных
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.company_service = CompanyService(db)
    
    def get_company_analytics(self, company_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Получение аналитики по компании за указанный период
        """
        # Проверяем существование компании
        company = self.company_service.get_company(company_id)
        if not company:
            return self.get_demo_analytics_data(start_date, end_date)
        
        # Получаем просмотры страниц
        page_views = self.db.query(PageView).filter(
            PageView.company_id == company_id,
            PageView.created_at.between(start_date, end_date)
        ).all()
        
        # Получаем действия пользователей
        user_actions = self.db.query(UserAction).filter(
            UserAction.company_id == company_id,
            UserAction.created_at.between(start_date, end_date)
        ).all()
        
        # Получаем бронирования
        bookings = self.db.query(Booking).filter(
            Booking.company_id == company_id,
            Booking.created_at.between(start_date, end_date)
        ).all()
        
        # Получаем источники трафика
        sources = self.db.query(SourceTracking).filter(
            SourceTracking.company_id == company_id,
            SourceTracking.created_at.between(start_date, end_date)
        ).all()
        
        # Получаем услуги компании
        services = self.company_service.get_company_services(company_id)
        
        # Если данных нет, возвращаем демо-данные
        if not page_views and not user_actions and not bookings:
            return self.get_demo_analytics_data(start_date, end_date)
        
        # Рассчитываем статистику
        total_views = len(page_views)
        total_actions = len(user_actions)
        total_bookings = len(bookings)
        
        # Конверсия из просмотра в действие и в бронирование
        action_conversion = (total_actions / total_views * 100) if total_views > 0 else 0
        booking_conversion = (total_bookings / total_views * 100) if total_views > 0 else 0
        
        # Среднее время на сайте
        avg_time_spent = 0
        if page_views:
            total_time = sum((pv.exit_time - pv.created_at).total_seconds() for pv in page_views if pv.exit_time)
            avg_time_spent = total_time / len(page_views) if len(page_views) > 0 else 0
        
        # Расчет статистики по дням
        daily_stats = self._calculate_daily_stats(page_views, user_actions, bookings, start_date, end_date)
        
        # Расчет статистики по услугам
        services_stats = self._calculate_services_stats(bookings, services)
        
        # Расчет статистики по источникам
        sources_stats = self._calculate_sources_stats(sources)
        
        return {
            "total_views": total_views,
            "total_actions": total_actions,
            "total_bookings": total_bookings,
            "action_conversion": round(action_conversion, 2),
            "booking_conversion": round(booking_conversion, 2),
            "avg_time_spent": round(avg_time_spent, 2),
            "daily_stats": daily_stats,
            "services_stats": services_stats,
            "sources_stats": sources_stats
        }
    
    def _calculate_daily_stats(
        self, 
        page_views: List[PageView], 
        user_actions: List[UserAction],
        bookings: List[Booking],
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Расчет статистики по дням
        """
        result = []
        current_date = start_date
        
        while current_date <= end_date:
            # Для текущего дня
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Фильтруем данные по текущему дню
            day_views = [pv for pv in page_views if day_start <= pv.created_at <= day_end]
            day_actions = [ua for ua in user_actions if day_start <= ua.created_at <= day_end]
            day_bookings = [b for b in bookings if day_start <= b.created_at <= day_end]
            
            # Расчет конверсии
            day_views_count = len(day_views)
            day_actions_count = len(day_actions)
            day_bookings_count = len(day_bookings)
            
            # Средняя выручка за день
            day_revenue = sum(b.price for b in day_bookings if b.price is not None)
            
            result.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "views": day_views_count,
                "actions": day_actions_count,
                "bookings": day_bookings_count,
                "revenue": day_revenue
            })
            
            # Переходим к следующему дню
            current_date += timedelta(days=1)
        
        return result
    
    def _calculate_services_stats(
        self, 
        bookings: List[Booking], 
        services: List[Service]
    ) -> List[Dict[str, Any]]:
        """
        Расчет статистики по услугам
        """
        # Словарь для хранения статистики по услугам
        services_stats = {}
        
        # Собираем данные по бронированиям услуг
        for booking in bookings:
            service_id = booking.service_id
            if service_id not in services_stats:
                # Находим услугу
                service = next((s for s in services if s.id == service_id), None)
                if not service:
                    continue
                
                services_stats[service_id] = {
                    "id": service_id,
                    "name": service.name,
                    "bookings_count": 0,
                    "revenue": 0
                }
            
            services_stats[service_id]["bookings_count"] += 1
            services_stats[service_id]["revenue"] += booking.price if booking.price is not None else 0
        
        # Преобразуем словарь в список
        result = list(services_stats.values())
        
        # Сортируем по количеству бронирований
        result.sort(key=lambda x: x["bookings_count"], reverse=True)
        
        return result
    
    def _calculate_sources_stats(self, sources: List[SourceTracking]) -> List[Dict[str, Any]]:
        """
        Расчет статистики по источникам трафика
        """
        # Словарь для хранения статистики по источникам
        sources_stats = {}
        
        # Собираем данные по источникам
        for source in sources:
            source_name = source.source
            if source_name not in sources_stats:
                sources_stats[source_name] = {
                    "name": source_name,
                    "count": 0
                }
            
            sources_stats[source_name]["count"] += 1
        
        # Преобразуем словарь в список
        result = list(sources_stats.values())
        
        # Сортируем по количеству
        result.sort(key=lambda x: x["count"], reverse=True)
        
        return result
    
    def get_demo_analytics_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Генерация демо-данных для аналитики
        """
        days_diff = (end_date - start_date).days + 1
        
        # Генерируем статистику по дням
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            # Генерируем случайные данные
            views = random.randint(50, 200)
            actions = random.randint(10, min(views, 100))
            bookings = random.randint(1, min(actions, 10))
            revenue = bookings * random.randint(1000, 5000)
            
            daily_stats.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "views": views,
                "actions": actions,
                "bookings": bookings,
                "revenue": revenue
            })
            
            # Переходим к следующему дню
            current_date += timedelta(days=1)
        
        # Генерируем статистику по услугам
        services_stats = []
        service_names = [
            "Стрижка мужская", "Стрижка женская", "Окрашивание", 
            "Маникюр", "Педикюр", "Массаж", "Уход за лицом"
        ]
        
        for i, name in enumerate(service_names):
            bookings_count = random.randint(5, 50)
            revenue = bookings_count * random.randint(1000, 3000)
            
            services_stats.append({
                "id": i + 1,
                "name": name,
                "bookings_count": bookings_count,
                "revenue": revenue
            })
        
        # Сортируем по количеству бронирований
        services_stats.sort(key=lambda x: x["bookings_count"], reverse=True)
        
        # Генерируем статистику по источникам
        sources_stats = [
            {"name": "Прямой переход", "count": random.randint(100, 500)},
            {"name": "Поисковые системы", "count": random.randint(200, 700)},
            {"name": "Социальные сети", "count": random.randint(50, 300)},
            {"name": "Реклама", "count": random.randint(30, 150)},
            {"name": "Другое", "count": random.randint(10, 50)}
        ]
        
        # Сортируем по количеству
        sources_stats.sort(key=lambda x: x["count"], reverse=True)
        
        # Рассчитываем общие показатели
        total_views = sum(day["views"] for day in daily_stats)
        total_actions = sum(day["actions"] for day in daily_stats)
        total_bookings = sum(day["bookings"] for day in daily_stats)
        
        # Конверсия
        action_conversion = (total_actions / total_views * 100) if total_views > 0 else 0
        booking_conversion = (total_bookings / total_views * 100) if total_views > 0 else 0
        
        # Среднее время на сайте (в секундах)
        avg_time_spent = random.randint(60, 300)
        
        return {
            "total_views": total_views,
            "total_actions": total_actions,
            "total_bookings": total_bookings,
            "action_conversion": round(action_conversion, 2),
            "booking_conversion": round(booking_conversion, 2),
            "avg_time_spent": avg_time_spent,
            "daily_stats": daily_stats,
            "services_stats": services_stats,
            "sources_stats": sources_stats
        }

    def _get_views_data(self, company_id: str, start_date: datetime, end_date: datetime) -> List[int]:
        """
        Получение данных о просмотрах компании по дням
        
        В будущей реализации данные будут запрашиваться из базы данных
        """
        days_count = (end_date - start_date).days + 1
        
        try:
            # Попытка получить реальные данные из БД
            # В реальной имплементации здесь будет SQL запрос
            # Сейчас используем демо-данные
            return self._generate_random_data(days_count, 10, 150)
        except Exception as e:
            logger.error(f"Ошибка при получении данных о просмотрах: {str(e)}")
            return self._generate_random_data(days_count, 10, 150)

    def _get_actions_data(self, company_id: str, start_date: datetime, end_date: datetime) -> List[int]:
        """
        Получение данных о действиях пользователей компании по дням
        
        В будущей реализации данные будут запрашиваться из базы данных
        """
        days_count = (end_date - start_date).days + 1
        
        try:
            # Попытка получить реальные данные из БД
            # В реальной имплементации здесь будет SQL запрос
            # Сейчас используем демо-данные
            return self._generate_random_data(days_count, 5, 50)
        except Exception as e:
            logger.error(f"Ошибка при получении данных о действиях: {str(e)}")
            return self._generate_random_data(days_count, 5, 50)

    def _get_services_data(self, company_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """
        Получение данных о популярности услуг компании
        
        В будущей реализации данные будут запрашиваться из базы данных
        """
        try:
            # В реальной имплементации здесь будет SQL запрос к таблице услуг
            # и связанным с ней таблицам статистики
            
            # Получаем услуги компании
            # В демо-версии используем временные данные
            services = ["Услуга 1", "Услуга 2", "Услуга 3", "Услуга 4", "Услуга 5"]
            services_data = self._generate_random_data(len(services), 20, 100)
            
            return {
                "labels": services,
                "data": services_data
            }
        except Exception as e:
            logger.error(f"Ошибка при получении данных о популярности услуг: {str(e)}")
            return {
                "labels": ["Услуга 1", "Услуга 2", "Услуга 3", "Услуга 4", "Услуга 5"],
                "data": self._generate_random_data(5, 20, 100)
            }

    def _get_sources_data(self, company_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """
        Получение данных об источниках трафика
        
        В будущей реализации данные будут запрашиваться из базы данных
        """
        try:
            # В реальной имплементации здесь будет SQL запрос к таблице
            # с источниками трафика и статистикой
            
            # В демо-версии возвращаем временные данные
            return {
                "labels": ["Поиск", "Рекомендации", "Прямые запросы", "Другое"],
                "data": [45, 25, 20, 10]
            }
        except Exception as e:
            logger.error(f"Ошибка при получении данных об источниках трафика: {str(e)}")
            return {
                "labels": ["Поиск", "Рекомендации", "Прямые запросы", "Другое"],
                "data": [45, 25, 20, 10]
            }

    def _get_avg_time(self, company_id: str, start_date: datetime, end_date: datetime) -> str:
        """
        Получение среднего времени пребывания на странице компании
        
        В будущей реализации данные будут запрашиваться из базы данных
        """
        try:
            # В реальной имплементации здесь будет SQL запрос
            # К таблице статистики посещений
            
            # В демо-версии генерируем случайное время
            minutes = random.randint(2, 10)
            seconds = random.randint(10, 59)
            
            return f"{minutes}:{seconds}"
        except Exception as e:
            logger.error(f"Ошибка при получении среднего времени пребывания: {str(e)}")
            return "3:45"

    def _generate_random_data(self, count: int, min_value: int, max_value: int) -> List[int]:
        """
        Генерация случайных данных для демонстрации
        """
        return [random.randint(min_value, max_value) for _ in range(count)] 
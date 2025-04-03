import logging
import aiohttp
from typing import Dict, Any, Optional, List, Tuple
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeoService:
    """Класс для работы с геолокационными сервисами"""
    
    def __init__(self):
        """Инициализация сервиса геолокации"""
        self.api_key = settings.YANDEX_MAPS_API_KEY
        self.geocode_url = "https://geocode-maps.yandex.ru/1.x/"
        
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Получение координат по адресу (прямое геокодирование)
        
        Args:
            address: Строка с адресом для геокодирования
            
        Returns:
            Словарь с информацией о геообъекте или None в случае ошибки
        """
        if not self.api_key:
            logger.warning("YANDEX_MAPS_API_KEY не настроен. Геокодирование невозможно.")
            return None
            
        params = {
            "apikey": self.api_key,
            "geocode": address,
            "format": "json",
            "results": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.geocode_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка API Яндекс.Карт: {response.status}")
                        return None
                        
                    data = await response.json()
                    
                    # Проверка наличия результатов
                    feature_members = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
                    if not feature_members:
                        logger.warning(f"Адрес не найден: {address}")
                        return None
                        
                    # Получение первого результата
                    geo_object = feature_members[0].get("GeoObject", {})
                    
                    # Получение координат (формат: "долгота широта")
                    point_str = geo_object.get("Point", {}).get("pos", "")
                    if not point_str:
                        logger.warning(f"Координаты не найдены для адреса: {address}")
                        return None
                        
                    # Преобразование строки координат в числа и меняем порядок (longitude, latitude)
                    longitude, latitude = map(float, point_str.split())
                    
                    # Формирование результата
                    result = {
                        "address": geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("text", ""),
                        "latitude": latitude,
                        "longitude": longitude,
                        "precision": geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("precision", ""),
                        "country": None,
                        "city": None,
                        "street": None,
                        "house": None
                    }
                    
                    # Получение компонентов адреса
                    address_components = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("Address", {}).get("Components", [])
                    for component in address_components:
                        kind = component.get("kind")
                        name = component.get("name")
                        if kind == "country":
                            result["country"] = name
                        elif kind == "locality":
                            result["city"] = name
                        elif kind == "street":
                            result["street"] = name
                        elif kind == "house":
                            result["house"] = name
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Ошибка при геокодировании адреса: {e}")
            return None
            
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Получение адреса по координатам (обратное геокодирование)
        
        Args:
            latitude: Широта
            longitude: Долгота
            
        Returns:
            Словарь с информацией о геообъекте или None в случае ошибки
        """
        if not self.api_key:
            logger.warning("YANDEX_MAPS_API_KEY не настроен. Обратное геокодирование невозможно.")
            return None
            
        # Формат для Яндекс: "долгота,широта"
        point = f"{longitude},{latitude}"
        
        params = {
            "apikey": self.api_key,
            "geocode": point,
            "format": "json",
            "results": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.geocode_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка API Яндекс.Карт: {response.status}")
                        return None
                        
                    data = await response.json()
                    
                    # Проверка наличия результатов
                    feature_members = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
                    if not feature_members:
                        logger.warning(f"Адрес не найден для координат: {latitude}, {longitude}")
                        return None
                        
                    # Получение первого результата
                    geo_object = feature_members[0].get("GeoObject", {})
                    
                    # Формирование результата
                    result = {
                        "address": geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("text", ""),
                        "latitude": latitude,
                        "longitude": longitude,
                        "precision": geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("precision", ""),
                        "country": None,
                        "city": None,
                        "street": None,
                        "house": None
                    }
                    
                    # Получение компонентов адреса
                    address_components = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("Address", {}).get("Components", [])
                    for component in address_components:
                        kind = component.get("kind")
                        name = component.get("name")
                        if kind == "country":
                            result["country"] = name
                        elif kind == "locality":
                            result["city"] = name
                        elif kind == "street":
                            result["street"] = name
                        elif kind == "house":
                            result["house"] = name
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Ошибка при обратном геокодировании: {e}")
            return None
            
    async def calculate_distance(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Optional[Dict[str, Any]]:
        """
        Расчет расстояния и времени в пути между двумя точками
        
        Args:
            start_lat: Широта начальной точки
            start_lon: Долгота начальной точки
            end_lat: Широта конечной точки
            end_lon: Долгота конечной точки
            
        Returns:
            Словарь с информацией о маршруте или None в случае ошибки
        """
        if not self.api_key:
            logger.warning("YANDEX_MAPS_API_KEY не настроен. Расчет расстояния невозможен.")
            return None
            
        # Использование API маршрутизации Яндекс.Карт
        route_url = "https://api.routing.yandex.net/v2/route"
        
        params = {
            "apikey": self.api_key,
            "waypoints": f"{start_lon},{start_lat}|{end_lon},{end_lat}",
            "mode": "driving"  # Можно изменить на "walking", "cycling" и т.д.
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(route_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка API маршрутизации Яндекс.Карт: {response.status}")
                        return None
                        
                    data = await response.json()
                    
                    # Извлечение информации о маршруте
                    route = data.get("route", {})
                    
                    # Формирование результата
                    result = {
                        "distance_meters": route.get("distance", {}).get("value", 0),
                        "duration_seconds": route.get("duration", {}).get("value", 0),
                        "start_point": f"{start_lat},{start_lon}",
                        "end_point": f"{end_lat},{end_lon}"
                    }
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Ошибка при расчете расстояния: {e}")
            return None
            
    async def get_nearest_locations(self, latitude: float, longitude: float, locations: List[Dict[str, Any]], 
                              max_distance_km: float = 10.0, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Получение ближайших локаций из списка
        
        Args:
            latitude: Широта текущей позиции
            longitude: Долгота текущей позиции
            locations: Список локаций с координатами (должны содержать поля latitude и longitude)
            max_distance_km: Максимальное расстояние для фильтрации в километрах
            limit: Максимальное количество возвращаемых локаций
            
        Returns:
            Список ближайших локаций с дополнительной информацией о расстоянии
        """
        from geopy.distance import geodesic
        
        # Расчет расстояния для каждой локации
        locations_with_distance = []
        
        for location in locations:
            loc_lat = location.get("latitude")
            loc_lon = location.get("longitude")
            
            if loc_lat is None or loc_lon is None:
                continue
                
            # Расчет расстояния между точками
            distance = geodesic((latitude, longitude), (loc_lat, loc_lon)).kilometers
            
            # Фильтрация по максимальному расстоянию
            if distance <= max_distance_km:
                # Добавление информации о расстоянии к локации
                location_with_distance = {**location, "distance_km": distance}
                locations_with_distance.append(location_with_distance)
                
        # Сортировка по расстоянию и ограничение количества
        sorted_locations = sorted(locations_with_distance, key=lambda x: x["distance_km"])[:limit]
        
        return sorted_locations

# Создание синглтона сервиса геолокации
geo_service = GeoService() 
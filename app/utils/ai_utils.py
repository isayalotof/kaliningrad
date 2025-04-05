"""
Утилиты для работы с AI сервисами
"""
import os
import json
import time
import base64
import requests
from pathlib import Path
from fastapi import UploadFile
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
# Настраиваем уровень логирования
logging.basicConfig(level=logging.DEBUG)

class FusionBrainAPI:
    """Класс для взаимодействия с Fusion Brain API (Kandinsky 3.1)"""

    def __init__(self):
        """Инициализация с загрузкой API ключей из переменных окружения"""
        load_dotenv()
        self.URL = "https://api-key.fusionbrain.ai/"
        self.API_KEY = os.getenv("FUSION_BRAIN_API_KEY", "")
        self.SECRET_KEY = os.getenv("FUSION_BRAIN_SECRET_KEY", "")
        
        self.AUTH_HEADERS = {
            'X-Key': f'Key {self.API_KEY}',
            'X-Secret': f'Secret {self.SECRET_KEY}',
        }
        
        logger.debug(f"API ключи: длина Key = {len(self.API_KEY)}, длина Secret = {len(self.SECRET_KEY)}")
        
        if not self.API_KEY or not self.SECRET_KEY:
            logger.warning("API ключи для Fusion Brain не настроены")

    def get_pipeline(self):
        """Получение ID модели Kandinsky 3.1"""
        try:
            logger.debug(f"Отправка запроса на {self.URL}key/api/v1/pipelines с заголовками: {self.AUTH_HEADERS}")
            response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
            
            if response.status_code != 200:
                logger.error(f"Ошибка получения pipeline ID: статус {response.status_code}, ответ: {response.text}")
                return None
                
            data = response.json()
            logger.debug(f"Получен ответ: {data}")
            
            if not data or len(data) == 0:
                logger.error("Полученный список pipelines пуст")
                return None
                
            return data[0]['id']
        except Exception as e:
            logger.error(f"Ошибка получения pipeline ID: {str(e)}")
            return None

    async def generate_image(self, prompt, width=1024, height=1024, style=None):
        """
        Генерация изображения по текстовому описанию
        
        Args:
            prompt: Текстовое описание изображения
            width: Ширина изображения (рекомендуется кратная 64)
            height: Высота изображения (рекомендуется кратная 64)
            style: Стиль изображения (опционально)
            
        Returns:
            Путь к сохраненному изображению или None в случае ошибки
        """
        try:
            # Получаем pipeline ID
            pipeline_id = self.get_pipeline()
            logger.debug(f"Полученный pipeline_id: {pipeline_id}")
            
            if not pipeline_id:
                return None
                
            # Подготовка параметров для запроса
            params = {
                "type": "GENERATE",
                "numImages": 1,
                "width": width,
                "height": height,
                "generateParams": {
                    "query": prompt
                }
            }
            
            # Добавляем стиль, если он указан
            if style:
                params["style"] = style
                
            logger.debug(f"Параметры запроса: {params}")
            
            # Отправляем запрос на генерацию
            data = {
                'pipeline_id': (None, pipeline_id),
                'params': (None, json.dumps(params), 'application/json')
            }
            
            logger.debug(f"Отправка POST запроса на {self.URL}key/api/v1/pipeline/run")
            response = requests.post(
                self.URL + 'key/api/v1/pipeline/run', 
                headers=self.AUTH_HEADERS, 
                files=data
            )
            
            if response.status_code != 201:
                logger.error(f"Ошибка при создании задачи генерации: статус {response.status_code}, ответ: {response.text}")
                return None
                
            # Получаем UUID задачи
            task_data = response.json()
            logger.debug(f"Ответ на запрос генерации: {task_data}")
            
            task_uuid = task_data.get('uuid')
            
            if not task_uuid:
                logger.error(f"Ошибка при создании задачи генерации: {task_data}")
                return None
                
            logger.debug(f"Получен UUID задачи: {task_uuid}")
                
            # Проверяем статус задачи
            image_data = await self.check_generation_status(task_uuid)
            
            if image_data:
                # Сохраняем изображение
                return await self.save_generated_image(image_data)
                
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при генерации изображения: {str(e)}")
            return None
    
    async def check_generation_status(self, task_uuid, max_attempts=30, delay=5):
        """
        Проверка статуса задачи генерации изображения
        
        Args:
            task_uuid: UUID задачи
            max_attempts: Максимальное количество попыток
            delay: Задержка между попытками в секундах
            
        Returns:
            Данные сгенерированного изображения в формате base64 или None
        """
        attempts = 0
        
        while attempts < max_attempts:
            try:
                logger.debug(f"Проверка статуса задачи {task_uuid}, попытка {attempts+1}")
                response = requests.get(
                    self.URL + 'key/api/v1/pipeline/status/' + task_uuid, 
                    headers=self.AUTH_HEADERS
                )
                
                if response.status_code != 200:
                    logger.error(f"Ошибка при проверке статуса: статус {response.status_code}, ответ: {response.text}")
                    attempts += 1
                    time.sleep(delay)
                    continue
                
                data = response.json()
                logger.debug(f"Ответ на запрос статуса: {data}")
                
                status = data.get('status')
                logger.debug(f"Статус задачи: {status}")
                
                if status == 'DONE':
                    # Проверяем, есть ли результат
                    if data.get('result') and data['result'].get('files'):
                        logger.debug(f"Задача завершена успешно, получены данные изображения")
                        return data['result']['files'][0]  # Берем первое изображение
                    else:
                        logger.error("Задача завершена, но изображения не найдены")
                        return None
                
                elif status == 'FAIL':
                    error = data.get('errorDescription', 'Неизвестная ошибка')
                    logger.error(f"Ошибка генерации изображения: {error}")
                    return None
                
                # Статус INITIAL или PROCESSING, продолжаем ожидание
                logger.debug(f"Задача в процессе выполнения (статус: {status}), ожидаем {delay} секунд")
                attempts += 1
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Ошибка при проверке статуса генерации: {str(e)}")
                attempts += 1
                time.sleep(delay)
        
        logger.error(f"Превышено максимальное количество попыток ({max_attempts})")
        return None
    
    async def save_generated_image(self, base64_data):
        """
        Сохранение сгенерированного изображения из base64
        
        Args:
            base64_data: Данные изображения в формате base64
            
        Returns:
            Путь к сохраненному изображению
        """
        try:
            # Создаем директорию для сохранения если ее нет
            upload_dir = Path("app/static/uploads/generated_logos")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Генерируем уникальное имя файла
            filename = f"logo_{int(time.time())}.png"
            file_path = upload_dir / filename
            
            logger.debug(f"Сохраняем изображение в: {file_path}")
            
            # Декодируем base64 и сохраняем изображение
            image_data = base64.b64decode(base64_data)
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # Возвращаем путь относительно директории static
            result_path = str(Path("uploads/generated_logos") / filename)
            logger.debug(f"Путь к сохраненному изображению: {result_path}")
            return result_path
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении сгенерированного изображения: {str(e)}")
            return None

    @staticmethod
    def create_logo_prompt(description):
        """
        Создание промпта для генерации логотипа на основе описания бизнеса
        
        Args:
            description: Описание бизнеса
            
        Returns:
            Промпт для генерации логотипа
        """
        if not description or len(description) < 5:
            return "Минималистичный современный логотип для бизнеса"
        
        # Базовый промпт для логотипа на русском языке
        base_prompt = "Создай современный, профессиональный логотип для бизнеса. "
        base_prompt += "Логотип должен быть минималистичным, запоминающимся и масштабируемым. "
        base_prompt += f"Бизнес занимается: {description}. "
        base_prompt += "Логотип на прозрачном фоне, без текста, яркий и стильный."
        
        return base_prompt 
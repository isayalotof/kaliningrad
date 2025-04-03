import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile

async def save_uploaded_file(upload_file: UploadFile, directory: str) -> str:
    """
    Сохраняет загруженный файл в указанную директорию.
    
    Args:
        upload_file: Загруженный файл
        directory: Директория для сохранения (относительно static/uploads)
        
    Returns:
        Путь к сохраненному файлу относительно static
    """
    # Создаем базовую директорию для загрузок если ее нет
    base_upload_dir = Path("app/static/uploads")
    target_dir = base_upload_dir / directory
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем уникальное имя файла
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Путь для сохранения
    file_path = target_dir / unique_filename
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        # Читаем файл чанками для экономии памяти
        shutil.copyfileobj(upload_file.file, buffer)
    
    # Возвращаем путь относительно директории static
    return str(Path("uploads") / directory / unique_filename) 
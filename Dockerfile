FROM python:3.11-slim

WORKDIR /app

# Установка необходимых системных зависимостей
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Создаем директории если их нет
RUN mkdir -p app/static/css app/static/js app/static/img

# Делаем entrypoint скрипт исполняемым
RUN chmod +x docker-entrypoint.sh

# Устанавливаем правильные разрешения для файлов
RUN chmod -R 755 app

EXPOSE 8080

# Использование entrypoint скрипта
ENTRYPOINT ["./docker-entrypoint.sh"]

# Запасной вариант, если entrypoint не сработает
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 
#!/bin/bash
set -e

echo "Starting Qwerty.town application initialization..."

# Ожидание, пока PostgreSQL запустится
echo "Waiting for PostgreSQL..."
sleep 5  # Даем время для инициализации контейнера
while ! nc -z db 5432; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL started"

# Проверка подключения к базе данных
echo "Testing database connection..."
python -c "
import psycopg2
from os import environ
try:
    conn = psycopg2.connect(environ.get('DATABASE_URL'))
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"

# Применение миграций Alembic
echo "Applying migrations..."
alembic upgrade head || {
    echo "Migration failed! Check database schema and connection"
    exit 1
}

# Отладочная информация
echo "===== DEBUG INFO ====="
echo "DATABASE_URL: $DATABASE_URL"
echo "HOST: $HOST"
echo "PORT: $PORT"
echo "======================"

# Запуск приложения
echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port 8080 --reload 
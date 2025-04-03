#!/bin/bash

echo "Перезапуск приложения Qwerty.town..."

# Остановка и удаление контейнеров
echo "Останавливаем контейнеры..."
docker compose down

# Удаление образов
echo "Удаляем старые образы..."
docker rmi $(docker images -q qwertytown-app 2>/dev/null) || true

# Установка необходимых зависимостей в requirements.txt
echo "Проверяем наличие email-validator в requirements.txt..."
if ! grep -q "email-validator" requirements.txt; then
    echo "Добавляем email-validator в requirements.txt..."
    echo "email-validator==2.1.0" >> requirements.txt
fi

# Сборка и запуск
echo "Пересобираем и запускаем приложение..."
docker compose up -d --build

# Проверка статуса
echo "Статус контейнеров:"
docker compose ps

# Небольшая пауза для запуска сервиса
echo "Ожидаем запуск сервиса..."
sleep 5

# Проверка доступности
echo "Проверка доступности приложения:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/status || echo "Сервис недоступен"

echo ""
echo "Просмотр логов (Ctrl+C для выхода):"
docker compose logs -f app 
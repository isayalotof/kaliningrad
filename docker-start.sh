#!/bin/bash

# Цвета для красивого вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Запуск проекта Qwerty.town в Docker...${NC}"

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}Файл .env не найден. Создаем из примера...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Файл .env создан. Пожалуйста, проверьте настройки в этом файле.${NC}"
fi

# Запуск Docker Compose
echo -e "${YELLOW}Запуск контейнеров Docker...${NC}"
docker compose up -d --build

# Проверка статуса
echo -e "${YELLOW}Проверка статуса контейнеров...${NC}"
docker compose ps

echo -e "${GREEN}Проект запущен! Доступен по адресу http://localhost:8000${NC}"
echo -e "${YELLOW}Для просмотра логов используйте команду:${NC} docker compose logs -f"
echo -e "${YELLOW}Для остановки проекта используйте команду:${NC} ./docker-stop.sh" 
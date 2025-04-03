#!/bin/bash

# Цвета для красивого вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Остановка проекта Qwerty.town в Docker...${NC}"

# Остановка контейнеров
docker compose down

echo -e "${GREEN}Проект остановлен!${NC}"
echo -e "${YELLOW}Для запуска проекта используйте команду:${NC} ./docker-start.sh"
echo -e "${RED}Для полного удаления данных проекта (включая базу данных) используйте:${NC} docker compose down -v" 
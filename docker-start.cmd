@echo off
echo Запуск проекта Qwerty.town в Docker...

REM Проверка наличия .env файла
if not exist .env (
    echo Файл .env не найден. Создаем из примера...
    copy .env.example .env
    echo Файл .env создан. Пожалуйста, проверьте настройки в этом файле.
)

REM Запуск Docker Compose
echo Запуск контейнеров Docker...
docker compose up -d --build

REM Проверка статуса
echo Проверка статуса контейнеров...
docker compose ps

echo Проект запущен! Доступен по адресу http://localhost:8000
echo Для просмотра логов используйте команду: docker compose logs -f
echo Для остановки проекта используйте: docker-stop.cmd

pause 
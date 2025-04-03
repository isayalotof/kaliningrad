@echo off
echo Перезапуск приложения Qwerty.town...

REM Остановка и удаление контейнеров
echo Останавливаем контейнеры...
docker compose down

REM Удаление образов
echo Удаляем старые образы...
for /f "tokens=*" %%i in ('docker images -q qwertytown-app 2^>nul') do (
    docker rmi %%i
)

REM Установка необходимых зависимостей в requirements.txt
echo Проверяем наличие email-validator в requirements.txt...
findstr /c:"email-validator" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Добавляем email-validator в requirements.txt...
    echo email-validator==2.1.0 >> requirements.txt
)

REM Сборка и запуск
echo Пересобираем и запускаем приложение...
docker compose up -d --build

REM Проверка статуса
echo Статус контейнеров:
docker compose ps

echo.
echo Проверка доступности приложения:
curl -s -o nul -w "%%{http_code}" http://localhost:8080/status || echo "Сервис недоступен"

echo.
echo Просмотр логов (Ctrl+C для выхода):
docker compose logs -f app

pause 
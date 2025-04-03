@echo off
echo Остановка проекта Qwerty.town в Docker...

REM Остановка контейнеров
docker compose down

echo Проект остановлен!
echo Для запуска проекта используйте: docker-start.cmd
echo ВНИМАНИЕ! Для полного удаления данных проекта (включая базу данных) используйте: docker compose down -v

pause 
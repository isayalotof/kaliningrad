# Запуск проекта Qwerty.town в Docker

## Быстрый старт

### Linux/MacOS:
```bash
# Запуск
./docker-start.sh

# Остановка
./docker-stop.sh
```

### Windows:
```
# Запуск - двойной клик на файле:
docker-start.cmd

# Остановка - двойной клик на файле:
docker-stop.cmd
```

Приложение будет доступно по адресу: http://localhost:8000

## Необходимые компоненты
- Docker
- Docker Compose (современная версия, встроенная в Docker)

## Подготовка к запуску

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd qwertytown
```

2. Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```

3. Отредактируйте файл `.env`, установив необходимые переменные окружения:
```
# Основные настройки - можно оставить по умолчанию для разработки
DEBUG=True
SECRET_KEY=qwertytown_secret_key_change_in_production
PORT=8000
HOST=0.0.0.0

# Настройки для базы данных - оставьте как есть для работы с Docker
DATABASE_URL=postgresql://postgres:postgres@db:5432/qwertytown

# Установите токен для Telegram бота, если нужно
TELEGRAM_BOT_TOKEN=your_telegram_token_here
```

## Запуск проекта

1. Соберите и запустите контейнеры:
```bash
docker compose up -d --build
```

2. Проверьте, что контейнеры запущены:
```bash
docker compose ps
```

3. Откройте веб-приложение в браузере:
```
http://localhost:8000
```

4. Для просмотра логов:
```bash
docker compose logs -f
```

## Управление проектом

### Остановка контейнеров
```bash
docker compose down
```

### Остановка и удаление данных (базы данных)
```bash
docker compose down -v
```

### Перезапуск отдельного сервиса
```bash
docker compose restart app
```

### Выполнение миграций вручную
```bash
docker compose exec app alembic upgrade head
```

### Создание новой миграции
```bash
docker compose exec app alembic revision --autogenerate -m "описание миграции"
```

## Управление базой данных

Для доступа к PostgreSQL:
```bash
docker compose exec db psql -U postgres -d qwertytown
```

## RabbitMQ

Для доступа к панели управления RabbitMQ:
```
http://localhost:15672
```

Данные для входа:
- Логин: guest
- Пароль: guest

## Описание сервисов

В проекте используются следующие сервисы:

1. **app** - основное приложение на FastAPI
2. **db** - база данных PostgreSQL
3. **rabbitmq** - брокер сообщений для асинхронных задач и интеграций

## Troubleshooting

### Проблемы с доступом к базе данных
Если приложение не может подключиться к базе данных, проверьте:
- Статус контейнера с PostgreSQL: `docker compose ps db`
- Логи контейнера: `docker compose logs db`
- Правильность URL подключения в файле `.env`

### Ошибки при применении миграций
Если возникают ошибки при применении миграций:
```bash
docker compose exec app alembic downgrade base
docker compose exec app alembic upgrade head
``` 
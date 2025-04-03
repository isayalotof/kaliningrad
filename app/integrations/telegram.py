import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Awaitable
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from app.core.config import settings

logger = logging.getLogger(__name__)

class TelegramBot:
    """Класс для работы с Telegram ботом"""
    
    def __init__(self):
        """Инициализация бота"""
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN не настроен. Telegram бот не будет запущен.")
            self.bot = None
            self.application = None
            return
            
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Регистрация обработчиков команд
        self._register_handlers()
        
    def _register_handlers(self):
        """Регистрация обработчиков сообщений"""
        if not self.application:
            return
            
        # Базовые команды
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        
        # Обработчики для бронирования
        self.application.add_handler(CommandHandler("book", self.cmd_book))
        self.application.add_handler(CommandHandler("mybookings", self.cmd_my_bookings))
        
        # Обработчик callback запросов (для кнопок)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
    async def start(self):
        """Запуск бота"""
        if not self.application:
            return
            
        if settings.TELEGRAM_WEBHOOK_URL:
            # Настройка вебхука
            await self.bot.set_webhook(url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook")
            logger.info(f"Telegram бот запущен с вебхуком на {settings.TELEGRAM_WEBHOOK_URL}")
        else:
            # Запуск в режиме polling
            await self.application.initialize()
            await self.application.start()
            logger.info("Telegram бот запущен в режиме polling")
            
    async def stop(self):
        """Остановка бота"""
        if not self.application:
            return
            
        if settings.TELEGRAM_WEBHOOK_URL:
            await self.bot.delete_webhook()
        else:
            await self.application.stop()
        
        logger.info("Telegram бот остановлен")
        
    async def send_message(self, chat_id: int, text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Отправка сообщения пользователю"""
        if not self.bot:
            logger.warning("Попытка отправки сообщения без настроенного бота")
            return None
            
        try:
            return await self.bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            return None
            
    async def send_booking_confirmation(self, chat_id: int, booking_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Отправка подтверждения бронирования"""
        service_name = booking_data.get("service_name", "Услуга")
        date_time = booking_data.get("date_time", "Не указано")
        location = booking_data.get("location", "Не указано")
        
        text = (
            f"✅ Бронирование подтверждено\n\n"
            f"Услуга: {service_name}\n"
            f"Дата и время: {date_time}\n"
            f"Локация: {location}\n\n"
            f"Для отмены используйте команду /mybookings"
        )
        
        return await self.send_message(chat_id, text, parse_mode="HTML")
        
    async def send_booking_reminder(self, chat_id: int, booking_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Отправка напоминания о бронировании"""
        service_name = booking_data.get("service_name", "Услуга")
        date_time = booking_data.get("date_time", "Не указано")
        location = booking_data.get("location", "Не указано")
        
        text = (
            f"🔔 Напоминание о бронировании\n\n"
            f"Услуга: {service_name}\n"
            f"Дата и время: {date_time}\n"
            f"Локация: {location}\n\n"
            f"До встречи!"
        )
        
        return await self.send_message(chat_id, text, parse_mode="HTML")
        
    # Обработчики команд
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        user = update.effective_user
        await update.message.reply_html(
            f"Привет, {user.mention_html()}! 👋\n\n"
            f"Я бот Qwerty.town для бронирования услуг.\n"
            f"Используйте /help чтобы узнать, что я умею."
        )
        
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        help_text = (
            "🤖 <b>Доступные команды:</b>\n\n"
            "/book - Забронировать услугу\n"
            "/mybookings - Ваши бронирования\n"
            "/help - Справка по командам\n\n"
            "Для общения с оператором просто напишите сообщение."
        )
        await update.message.reply_html(help_text)
        
    async def cmd_book(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /book"""
        # Здесь будет логика показа доступных услуг и возможность бронирования
        await update.message.reply_text(
            "Функция бронирования пока в разработке.\n"
            "Скоро здесь появится возможность выбрать услугу и время!"
        )
        
    async def cmd_my_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /mybookings"""
        # Здесь будет логика показа бронирований пользователя
        await update.message.reply_text(
            "Функция просмотра бронирований пока в разработке.\n"
            "Скоро здесь появятся ваши бронирования!"
        )
        
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        # Получение данных из callback_data
        data = query.data
        
        # Обработка различных действий по кнопкам
        if data.startswith("book_"):
            service_id = data.replace("book_", "")
            await query.edit_message_text(
                f"Вы выбрали услугу с ID {service_id}.\n"
                f"Функция бронирования конкретной услуги пока в разработке."
            )
        elif data.startswith("cancel_"):
            booking_id = data.replace("cancel_", "")
            await query.edit_message_text(
                f"Вы отменили бронирование с ID {booking_id}.\n"
                f"Функция отмены бронирования пока в разработке."
            )
        
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений"""
        # Простой эхо-ответ для текстовых сообщений
        await update.message.reply_text(
            "Спасибо за ваше сообщение! В ближайшее время с вами свяжется наш оператор."
        )

# Создание синглтона бота
telegram_bot = TelegramBot()

# Асинхронная функция для запуска бота
async def start_bot():
    await telegram_bot.start()

# Асинхронная функция для остановки бота
async def stop_bot():
    await telegram_bot.stop() 
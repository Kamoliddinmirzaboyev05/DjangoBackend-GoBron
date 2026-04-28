"""Telegram bot asosiy fayli"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings

from .handlers import router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoBronBot:
    """GoBron Telegram Bot"""
    
    def __init__(self):
        self.bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        
        # Handlerlarni ro'yxatdan o'tkazish
        self.dp.include_router(router)
    
    async def start_polling(self):
        """Polling rejimida botni ishga tushirish"""
        try:
            logger.info("🤖 GoBron Bot ishga tushmoqda...")
            
            # Bot ma'lumotlarini olish
            bot_info = await self.bot.get_me()
            logger.info(f"Bot: @{bot_info.username} ({bot_info.full_name})")
            
            # Polling boshlash
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Bot ishga tushirishda xatolik: {e}")
            raise
        finally:
            await self.bot.session.close()
    
    async def stop(self):
        """Botni to'xtatish"""
        logger.info("🛑 Bot to'xtatilmoqda...")
        await self.bot.session.close()
    
    async def set_webhook(self, webhook_url):
        """Webhook o'rnatish"""
        try:
            await self.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook o'rnatildi: {webhook_url}")
        except Exception as e:
            logger.error(f"Webhook o'rnatishda xatolik: {e}")
            raise
    
    async def delete_webhook(self):
        """Webhook o'chirish"""
        try:
            await self.bot.delete_webhook()
            logger.info("✅ Webhook o'chirildi")
        except Exception as e:
            logger.error(f"Webhook o'chirishda xatolik: {e}")
            raise


# Bot instance
bot_instance = GoBronBot()


async def run_bot():
    """Botni ishga tushirish"""
    await bot_instance.start_polling()


def start_bot_sync():
    """Sinxron ravishda botni ishga tushirish"""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")
        raise
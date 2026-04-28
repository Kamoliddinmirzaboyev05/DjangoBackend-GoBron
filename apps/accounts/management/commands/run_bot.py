"""GoBron Bot ishga tushirish management command"""

import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.accounts.bot.bot import start_bot_sync

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'GoBron Telegram botini ishga tushirish (aiogram 3.x)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Debug rejimida ishga tushirish',
        )

    def handle(self, *args, **options):
        # Bot token tekshirish
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            self.stdout.write(
                self.style.ERROR('❌ TELEGRAM_BOT_TOKEN .env faylida sozlanmagan!')
            )
            return

        # Debug rejim
        if options['debug']:
            logging.getLogger().setLevel(logging.DEBUG)
            self.stdout.write(
                self.style.WARNING('🐛 Debug rejimi yoqildi')
            )

        # Bot ishga tushirish
        self.stdout.write(
            self.style.SUCCESS('🚀 GoBron Bot ishga tushmoqda...')
        )
        
        try:
            start_bot_sync()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Bot foydalanuvchi tomonidan to\'xtatildi')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Bot ishga tushirishda xatolik: {e}')
            )
            logger.exception("Bot error:")
            raise
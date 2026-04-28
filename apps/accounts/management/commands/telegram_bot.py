import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.accounts.bot.bot import start_bot_sync

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'GoBron Telegram botini ishga tushirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Webhook rejimida ishga tushirish',
        )
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='Webhook URL manzili',
        )

    def handle(self, *args, **options):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            self.stdout.write(
                self.style.ERROR('❌ TELEGRAM_BOT_TOKEN sozlanmagan!')
            )
            return

        if options['webhook']:
            webhook_url = options.get('webhook_url')
            if not webhook_url:
                self.stdout.write(
                    self.style.ERROR('❌ Webhook URL kiritilmagan!')
                )
                return
            
            self.setup_webhook(webhook_url)
        else:
            self.start_polling()

    def setup_webhook(self, webhook_url):
        """Webhook o'rnatish"""
        import asyncio
        from apps.accounts.bot.bot import bot_instance
        
        async def set_webhook():
            await bot_instance.set_webhook(webhook_url)
        
        try:
            asyncio.run(set_webhook())
            self.stdout.write(
                self.style.SUCCESS(f'✅ Webhook o\'rnatildi: {webhook_url}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Webhook o\'rnatishda xatolik: {e}')
            )

    def start_polling(self):
        """Polling rejimida bot ishga tushirish"""
        self.stdout.write(
            self.style.SUCCESS('🤖 GoBron Bot ishga tushmoqda (Polling)...')
        )
        
        try:
            start_bot_sync()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('🛑 Bot to\'xtatildi')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Bot xatolik: {e}')
            )
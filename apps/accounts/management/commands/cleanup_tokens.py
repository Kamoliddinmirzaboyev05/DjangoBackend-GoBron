"""Eski va yaroqsiz tokenlarni tozalash management command"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from apps.accounts.models import MagicToken


class Command(BaseCommand):
    help = 'Eski va yaroqsiz Magic Tokenlarni tozalash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Barcha tokenlarni o\'chirish (ehtiyotkorlik bilan)',
        )
        parser.add_argument(
            '--expired-only',
            action='store_true',
            help='Faqat muddati tugagan tokenlarni o\'chirish',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Barcha tokenlarni o'chirish
            count = MagicToken.objects.count()
            MagicToken.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Barcha {count} ta token o\'chirildi')
            )
            
        elif options['expired_only']:
            # Faqat muddati tugagan tokenlarni o'chirish
            expired_tokens = MagicToken.objects.filter(
                expires_at__lt=timezone.now()
            )
            count = expired_tokens.count()
            expired_tokens.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ {count} ta muddati tugagan token o\'chirildi')
            )
            
        else:
            # Yaroqsiz tokenlarni o'chirish (default)
            now = timezone.now()
            
            # Muddati tugagan tokenlar
            expired_count = MagicToken.objects.filter(expires_at__lt=now).count()
            MagicToken.objects.filter(expires_at__lt=now).delete()
            
            # Limit tugagan tokenlar
            limit_exceeded = MagicToken.objects.filter(
                usage_count__gte=models.F('max_usage')
            )
            limit_count = limit_exceeded.count()
            limit_exceeded.delete()
            
            total_cleaned = expired_count + limit_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Tozalash tugallandi:\n'
                    f'   - Muddati tugagan: {expired_count} ta\n'
                    f'   - Limit tugagan: {limit_count} ta\n'
                    f'   - Jami tozalangan: {total_cleaned} ta'
                )
            )
            
            # Qolgan faol tokenlar
            active_count = MagicToken.objects.filter(
                expires_at__gt=now,
                usage_count__lt=models.F('max_usage')
            ).count()
            
            self.stdout.write(
                self.style.WARNING(f'ℹ️ Faol tokenlar qoldi: {active_count} ta')
            )
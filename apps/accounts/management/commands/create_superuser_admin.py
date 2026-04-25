from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a default superuser admin account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@football.uz')
        parser.add_argument('--password', type=str, default='Admin@12345')
        parser.add_argument('--phone', type=str, default='+998901234567')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        phone = options['phone']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'User "{username}" already exists. Skipping creation.'
                )
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin',
            phone=phone,
            role='admin',
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'  Username : {user.username}\n'
                f'  Email    : {user.email}\n'
                f'  Password : {password}\n'
                f'  Role     : {user.role}\n'
                f'\nPlease change the password after first login!'
            )
        )

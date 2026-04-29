from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a default superuser admin account'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, default='+998901234567')
        parser.add_argument('--email', type=str, default='admin@gobron.uz')
        parser.add_argument('--password', type=str, default='Admin@12345')
        parser.add_argument('--name', type=str, default='Super Admin')

    def handle(self, *args, **options):
        phone_number = options['phone']
        email = options['email']
        password = options['password']
        full_name = options['name']

        if User.objects.filter(phone_number=phone_number).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'User with phone "{phone_number}" already exists. Skipping creation.'
                )
            )
            return

        user = User.objects.create_superuser(
            phone_number=phone_number,
            email=email,
            password=password,
            full_name=full_name,
            user_role='OWNER',
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'  Phone    : {user.phone_number}\n'
                f'  Email    : {user.email}\n'
                f'  Name     : {user.full_name}\n'
                f'  Password : {password}\n'
                f'  Role     : {user.get_user_role_display()}\n'
                f'\nPlease change the password after first login!'
            )
        )

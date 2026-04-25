from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Foydalanuvchi'),
        ('admin', 'Admin'),
    ]

    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='Rol'
    )
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='Avatar'
    )

    # email ixtiyoriy
    email = models.EmailField(blank=True, null=True, verbose_name='Email')

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin_role(self):
        return self.role == 'admin'

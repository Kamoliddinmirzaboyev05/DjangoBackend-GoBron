from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from apps.fields.models import FootballField
import datetime

@receiver(post_save, sender=CustomUser)
def create_owner_field(sender, instance, created, **kwargs):
    """
    Agar foydalanuvchi roli 'OWNER' bo'lsa, unga avtomatik ravishda 
    yangi futbol maydoni biriktiriladi (agar hali yo'q bo'lsa).
    """
    if instance.user_role == 'OWNER' and created:
        # Agar owner uchun hali maydon yaratilmagan bo'lsa
        if not FootballField.objects.filter(owner=instance).exists():
            FootballField.objects.create(
                owner=instance,
                name=f"{instance.full_name or instance.phone_number} maydoni",
                address="Manzil kiritilmagan",
                city="Shahar kiritilmagan",
                price_per_hour=0,
                opening_time=datetime.time(8, 0),
                closing_time=datetime.time(23, 0),
            )

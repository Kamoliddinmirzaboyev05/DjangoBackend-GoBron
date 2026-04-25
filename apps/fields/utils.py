from datetime import datetime, date, timedelta
from .models import TimeSlot


def generate_slots_for_field_date(field, slot_date):
    """
    Berilgan maydon va sana uchun 1 soatlik slotlarni yaratadi.
    Agar opening_time > closing_time bo'lsa (masalan 08:00 → 02:00),
    tunni kesib o'tadi deb hisoblanadi.
    Mavjud slotlar qayta yaratilmaydi.
    """
    opening = field.opening_time
    closing = field.closing_time

    base = datetime.combine(slot_date, opening)

    # Agar closing <= opening — tunni kesib o'tadi (masalan 08:00 → 02:00 ertasi kun)
    if closing <= opening:
        close_dt = datetime.combine(slot_date + timedelta(days=1), closing)
    else:
        close_dt = datetime.combine(slot_date, closing)

    slots_to_create = []
    current = base
    while current < close_dt:
        next_dt = current + timedelta(hours=1)
        if next_dt > close_dt:
            break
        exists = TimeSlot.objects.filter(
            field=field,
            date=slot_date,
            start_time=current.time(),
        ).exists()
        if not exists:
            slots_to_create.append(TimeSlot(
                field=field,
                date=slot_date,
                start_time=current.time(),
                end_time=next_dt.time(),
                is_active=True,
                is_booked=False,
            ))
        current = next_dt

    if slots_to_create:
        TimeSlot.objects.bulk_create(slots_to_create)

    return TimeSlot.objects.filter(field=field, date=slot_date).order_by('start_time')


def get_available_dates(field):
    """
    Maydon uchun bugundan boshlab advance_booking_days kun ichidagi sanalar ro'yxati.
    """
    today = date.today()
    return [today + timedelta(days=i) for i in range(field.advance_booking_days)]

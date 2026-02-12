from django.utils import timezone
from core.models import Booking, BookingStatus


def cancel_expired_bookings():
    now = timezone.now()

    Booking.objects.filter(
        status=BookingStatus.PENDING,
        expires_at__lt=now
    ).update(status=BookingStatus.CANCELLED)
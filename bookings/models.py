from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
# Create your models here.

User = get_user_model()

def default_expires_at():
    return timezone.now() + timedelta(minutes=15)

class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'
    CONFIRMED = 'confirmed', 'Confirmed'
    CLIENT_NOT_CONFIRMED = 'client_not_confirmed', 'Client not confirmed'
    CANCELLED = 'cancelled', 'Cancelled'
    COMPLETED = 'completed', 'Completed'


class PaymentType(models.TextChoices):
    CASH = 'cash', 'Cash'
    CARD = 'card', 'Card'





class Booking(models.Model):
    user_id = models.PositiveIntegerField()    
    master_id = models.PositiveIntegerField()

    service_type = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()

    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,    
        default=PaymentType.CARD
    )

    status = models.CharField(
        max_length=30,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )

    expires_at = models.DateTimeField(null=False)
    reject_reason = models.TextField(null=True, blank=True)
    client_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # faqat yaratishda
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)


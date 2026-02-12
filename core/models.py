from django.db import models



class Master(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    )
    SERVICE_TYPES = (
        ('barber', 'Barber'),
        ('beard', 'Beard'),
        ('haircut', 'Haircut'),
        ('planting', 'Planting'),

    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='barber')
    service_types = models.JSONField(default=list, blank=True)  # Usta bir nechta xizmat ko‘rsatishi mumkin
    price = models.PositiveIntegerField(default=0)  # xizmat narxi
    experience_years = models.PositiveIntegerField()
    rating = models.FloatField(default=0)

    about = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class MasterLocation(models.Model):
    master = models.OneToOneField(
        Master,
        on_delete=models.CASCADE,
        related_name='master_location'
    )
    lat = models.FloatField()  #latitude- kenglik
    lng = models.FloatField()  #longitude-uzunlik
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    place_id = models.CharField(max_length=255)
    accuracy = models.IntegerField()


class MasterAvailability(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    date = models.DateField()
    available_slots = models.JSONField()  # mavjud bo'lgan vaqt slotlari ro'yxati
    discount_percent = models.PositiveIntegerField(default=0)  # chegirma foizi

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('master', 'date')

    def __str__(self):
        return f"{self.master.full_name} - {self.date}"
    
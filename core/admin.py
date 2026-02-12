from django.contrib import admin
from .models import Master, MasterLocation, MasterAvailability

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'service_type',
        'rating',
        'status',
        'created_at'
    )
    list_filter = ('service_type', 'status')
    search_fields = ('full_name', 'phone')


@admin.register(MasterLocation)
class MasterLocationAdmin(admin.ModelAdmin):
    list_display = ('master', 'district', 'lat', 'lng')


@admin.register(MasterAvailability)
class MasterAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        'master',
        'date',
        'discount_percent'
    )
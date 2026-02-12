from rest_framework import serializers
from .models import Booking
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
import random


class BookingCreateSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    time = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])

    class Meta:
        model = Booking
        fields = ['user_id', 'master_id', 'service_type', 'date', 'time', 'payment_type']

    def validate(self, data):
        date = data.get("date")
        time = data.get("time")
        booking_datetime = datetime.combine(date, time)
        booking_datetime = timezone.make_aware(booking_datetime, timezone.get_current_timezone())

        if booking_datetime < timezone.now():
            raise serializers.ValidationError("Booking time cannot be in the past.")

        # Ikki marta band qilishni oldini olish
        master_id = data.get("master_id")
        if Booking.objects.filter(
            master_id=master_id,
            date=date,
            time=time,
            status__in=["pending", "accepted", "confirmed"]
        ).exists():
            raise serializers.ValidationError("This time slot is already booked for the selected master.")

        return data

    def validate_time(self, value):
        return value.replace(second=0, microsecond=0)
    


class BookingResponseSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source='id', read_only=True)
    status = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = Booking
        fields = ['booking_id', 'status', 'expires_at']
    
    


class BookingMasterActionSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(read_only=True, source='id')
    reason = serializers.CharField(source='reject_reason', required=False, allow_null=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'status', 'reason']


    def validate(self, attrs):
        status_value = attrs.get('status')
        reason_value = attrs.get('reject_reason')

        if status_value == 'rejected' and not reason_value:
            raise serializers.ValidationError("Rejected qilganiz uchun sabab kiritishingiz kerak.")
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status == 'accepted':
            data.pop('reason', None)  
        return data


class BookingClientConfirmSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(read_only=True, source='id')
    status = serializers.CharField(read_only=True)
    client_confirmed = serializers.BooleanField(required=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'status', 'client_confirmed']

    def validate_client_confirmed(self, value):
        booking = self.instance
        if not booking:
            raise serializers.ValidationError("Booking topilmadi.")

        # Booking datetime ni yaratish
        booking_datetime = datetime.combine(booking.date, booking.time)
        if timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime, timezone.get_current_timezone())

        now = timezone.localtime()  # Hozirgi vaqtni localtime bilan olish
        time_diff = booking_datetime - now

        if time_diff.total_seconds() < 0:
            raise serializers.ValidationError("Bu buyurtma vaqti allaqachon o'tgan.")
        # if time_diff.total_seconds() > 60 * 60:
        #     raise serializers.ValidationError("Faqat buyurtmadan 60 daqiqa oldin tasdiqlashingiz mumkin.")
        if time_diff.total_seconds() < 30 * 60:
            raise serializers.ValidationError("Faqat buyurtmadan 30 daqiqa oldin tasdiqlashingiz mumkin.")

        return value
    

class BookingCompleteSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source='id', read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'status']

    def validate(self, data):
        booking = self.instance

        if booking.status not in ['accepted', 'confirmed']:
            raise serializers.ValidationError( "Faqat qabul qilingan yoki tasdiqlangan buyurtmani tugatish mumkin.")

        return data

    def update(self, instance, validated_data):
        instance.status = 'completed'
        instance.save()
        return instance
from rest_framework import serializers

from core.utils import calculate_distance_km, get_master_availability
from .models import Master, MasterLocation, MasterAvailability


class MasterLocationSerializer(serializers.ModelSerializer): #master location uchun
    class Meta:
        model = MasterLocation
        fields = (
            'lat', 
            'lng', 
            'address', 
            'district', 
            'place_id', 
            'accuracy'
            )


class MasterCreateSerializer(serializers.ModelSerializer): #master yaratish uchun
    master_location = MasterLocationSerializer(write_only=True)

    class Meta:
        model = Master
        fields = (
            'id',
            'full_name',
            'phone',
            'service_type',
            'service_types',
            'price',
            'experience_years',
            'about',
            'avatar_url',
            'status',
            'created_at',
            'master_location',
        )

        read_only_fields = ('id', 'status', 'created_at')
    
    def validate_service_types(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("service_types list bo'lishi kerak.")
        
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"service_types[{idx}] obyekt bo'lishi kerak.")
            if "name" not in item or not item["name"]:
                raise serializers.ValidationError(f"service_types[{idx}].name kerak.")
            if "service_price" not in item:
                raise serializers.ValidationError(f"service_types[{idx}].service_price kerak.")
            price = item["service_price"]
            if not isinstance(price, int) or price < 0:
                raise serializers.ValidationError(
                    f"service_types[{idx}].service_price musbat son bo'lishi kerak."
                    )
        return value




    def create(self, validated_data):
        location_data = validated_data.pop('master_location')

        master = Master.objects.create(**validated_data) #usta yaratiladi
        MasterLocation.objects.create(master=master, **location_data)
        return master
    

class MasterListSerializer(serializers.ModelSerializer): #masterlarni filterlab olish uchun
    master_location = MasterLocationSerializer(read_only=True)
    discount_percent = serializers.SerializerMethodField()
    is_available_today = serializers.SerializerMethodField()
    next_available_time = serializers.SerializerMethodField()
    rating = serializers.FloatField()
    id = serializers.SerializerMethodField()




    class Meta:
        model = Master
        fields = (
            'id',
            'full_name',
            'service_type',
            'price',
            'rating',
            'master_location',
            'discount_percent',
            'is_available_today',
            'next_available_time',
            
        )
        
    
    # master mavjudligi uchun
    def get_is_available_today(self, obj):
        from core.utils import get_today_availability
        return get_master_availability(obj)["is_available_today"]
    
    def get_next_available_time(self, obj):
        from core.utils import get_today_availability
        return get_master_availability(obj)["next_available_time"]
    
    def get_discount_percent(self, obj):
        from core.utils import get_today_availability
        return get_master_availability(obj)["discount_percent"]
    
    def get_id(self, obj):
        return str(obj.id).zfill(5)  # ID ni 5 ta raqamga to'ldirish


class MasterAvailabilitySerializer(serializers.ModelSerializer):
        class Meta:
            model = MasterAvailability
            fields = (
                'date',
                'available_slots',
                'discount_percent',
            )


class MasterDetailSerializer(serializers.ModelSerializer):
    master_location = MasterLocationSerializer(read_only=True)
    discount_percent = serializers.SerializerMethodField()
    is_available_today = serializers.SerializerMethodField()
    next_available_time = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = Master
        fields = (
            'id',
            'full_name',
            'phone',
            'service_type',
            'service_types',
            'price',
            'experience_years',
            'rating',
            'avatar_url',
            'about',
            'master_location',
            'discount_percent',
            'is_available_today',
            'next_available_time',
        )

    def get_discount_percent(self, obj):
        return get_master_availability(obj)["discount_percent"]

    def get_is_available_today(self, obj):
        return get_master_availability(obj)["is_available_today"]

    def get_next_available_time(self, obj):
        return get_master_availability(obj)["next_available_time"]

    def get_id(self, obj):
        return str(obj.id).zfill(5)

from django.shortcuts import  render, get_object_or_404
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Booking
from .serializers import BookingCompleteSerializer, BookingCreateSerializer, BookingResponseSerializer, BookingMasterActionSerializer, BookingClientConfirmSerializer
from core.utils import cancel_expired_bookings





class BookingCreateView(CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer

    def create(self, request, *args, **kwargs):
        cancel_expired_bookings() 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        response_serializer = BookingResponseSerializer(booking)
        return Response(response_serializer.data, status=201)


class BookingMasterActionView(UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingMasterActionSerializer
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BookingClientConfirmAPIView(UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingClientConfirmSerializer
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        booking.client_confirmed = serializer.validated_data.get('client_confirmed', booking.client_confirmed)
        if booking.client_confirmed:
            booking.status = "confirmed"
        booking.save()

        return Response({
            "booking_id": booking.id,
            "status": booking.status
        })



class BookingCompleteAPIView(UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCompleteSerializer
    lookup_field = 'id'

    def patch(self, request, id):
        booking = get_object_or_404(Booking, id=id)

        serializer = BookingCompleteSerializer(
            booking,
            data={},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
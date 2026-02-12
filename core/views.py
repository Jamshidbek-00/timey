
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView
from .models import Master, MasterAvailability
from .serializers import MasterCreateSerializer, MasterListSerializer, MasterAvailabilitySerializer, MasterDetailSerializer
from .utils import get_today_availability, get_next_available_time
from django.shortcuts import get_object_or_404
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes






class TestAPIView(APIView):
    def get(self, request):
        return Response({
            "message": "Timey backend is working fine!"
        })
    

class MasterCreateAPIView(CreateAPIView): # master yaratish uchun
    queryset = Master.objects.all()
    serializer_class = MasterCreateSerializer



@extend_schema(
    parameters=[
        OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Sahifa raqami (1,2,3...)"),
        OpenApiParameter("size", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Har sahifada nechta master"),
        OpenApiParameter("service_type", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Masalan: barber"),
        OpenApiParameter("only_available", OpenApiTypes.BOOL, OpenApiParameter.QUERY, description="true bo‘lsa faqat bo‘shlar"),
        OpenApiParameter("sort", OpenApiTypes.STR, OpenApiParameter.QUERY, description="rating bo‘yicha tartib"),
    ]
)
class MasterListAPIView(APIView): #masterlarni filterlab olish uchun
    def get(self, request):
        masters = Master.objects.all()

        # service_type boyicha filterlash
        service_type = request.query_params.get('service_type', 'barber')
        masters = masters.filter(service_type=service_type)

        # faqat mavjud bo'lganlarni olish
        only_available = request.query_params.get('only_available')
        if only_available == 'true':
            masters = [
                m for m in masters
                if get_today_availability(m)["is_available_today"]
            ]
        
        #sort boyicha tartiblash
        sort = request.query_params.get('sort')
        if sort == 'rating':
            masters = masters.order_by('-rating')


        #pagination
        page = int(request.query_params.get('page', 1))
        size = int(request.query_params.get('size', 5))

        total = len(masters) if isinstance(masters, list) else masters.count()
        start = (page - 1) * size
        end = start + size

        masters_page = masters[start:end]



        serializer = MasterListSerializer(
            masters_page, 
            
            many = True, 
            context={'request': request}
            )
        
        return Response({
            "page": page,
            "size": size,
            "total": total,
            "results": serializer.data
        })
    
#
class MasterAvailabilityPatchAPIView(GenericAPIView):
    serializer_class = MasterAvailabilitySerializer

    def patch(self, request, master_id):
        master = get_object_or_404(Master, id=master_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        date = serializer.validated_data['date']

        availability, created = MasterAvailability.objects.update_or_create(
            master=master,
            date=date,
            defaults={
                'available_slots': serializer.validated_data['available_slots'],
                'discount_percent': serializer.validated_data.get('discount_percent', 0),
            }
        )

        return Response(
            {'success': True},
            status=status.HTTP_200_OK
        )


#master detail uchun
class MasterDetailAPIView(RetrieveAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterDetailSerializer
    lookup_field = 'id'  


#master keyingi mavjud vaqtni olish uchun
class MasterNextAvailableTimeAPIView(APIView):
    def get(self, request, master_id):
        master = get_object_or_404(Master, id=master_id)
        next_time = get_next_available_time(master)

        return Response({
            "master_id": str(master.id).zfill(5),
            "next_available_time": next_time
        })
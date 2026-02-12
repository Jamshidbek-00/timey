from django.urls import path
from .views import MasterListAPIView, MasterNextAvailableTimeAPIView, TestAPIView, MasterCreateAPIView, MasterAvailabilityPatchAPIView, MasterDetailAPIView

urlpatterns = [
    path('test/', TestAPIView.as_view()),
    path('masters/', MasterCreateAPIView.as_view()),
    path('masters/list/', MasterListAPIView.as_view()),
    path('masters/<int:master_id>/availability/', MasterAvailabilityPatchAPIView.as_view()),
    path('masters/<int:id>/', MasterDetailAPIView.as_view()),
    path('masters/<int:master_id>/next-available-time/', MasterNextAvailableTimeAPIView.as_view()),
]

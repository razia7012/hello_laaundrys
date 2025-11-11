from django.urls import path
from .views import ServiceListAPIView

urlpatterns = [
 path('services/', ServiceListAPIView.as_view(), name='service-list'),
 path('locations/', LocationListView.as_view(), name='locations'),
]

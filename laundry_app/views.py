from rest_framework import generics
from .models import Service
from .serializers import ServiceSerializer

class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer

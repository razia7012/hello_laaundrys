from rest_framework import generics
from .models import Service, Country
from .serializers import ServiceSerializer, CountryWithCitiesSerializer, LaundrySerializer
from rest_framework.response import Response
from rest_framework import status

class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer

class LocationListView(generics.GenericAPIView):
    serializer_class = CountryWithCitiesSerializer

    def get(self, request):
        country_name = request.query_params.get('country')
        if country_name:
            try:
                country = Country.objects.get(name__iexact=country_name)
                serializer = self.get_serializer(country)
                return Response(serializer.data)
            except Country.DoesNotExist:
                return Response({"detail": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            countries = Country.objects.all()
            serializer = self.get_serializer(countries, many=True)
            return Response(serializer.data)

class LaundryListByCityView(generics.ListAPIView):
    serializer_class = LaundrySerializer

    def get_queryset(self):
        city_name = self.request.query_params.get('city')
        if city_name:
            return Laundry.objects.filter(city__name__iexact=city_name, is_active=True)
        return Laundry.objects.none()

class LaundryCreateView(generics.CreateAPIView):
    queryset = Laundry.objects.all()
    serializer_class = LaundryCreateSerializer
    permission_classes = [IsAuthenticated]

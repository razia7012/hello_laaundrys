from rest_framework import generics
from .models import Service, Country
from .serializers import ServiceSerializer, CountryWithCitiesSerializer
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
from rest_framework import serializers
from .models import Service, Country, City

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'starting_price', 'is_active']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class CountryWithCitiesSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'name', 'cities']

class LaundrySerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    country_name = serializers.CharField(source='city.country.name', read_only=True)

    class Meta:
        model = Laundry
        fields = [
            'id', 'name', 'city_name', 'country_name',
            'address', 'contact_number', 'email',
            'opening_hours', 'rating', 'is_active'
        ]

class LaundryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laundry
        fields = [
            'id',
            'name',
            'city',
            'address',
            'contact_number',
            'email',
            'opening_hours',
            'rating',
            'is_active'
        ]
from django.core.management.base import BaseCommand
from locations.models import Country, City

#python manage.py load_gcc_data
class Command(BaseCommand):
    help = "Load GCC countries and their main cities into the database"

    def handle(self, *args, **options):
        data = {
            "Qatar": ["Doha", "Al Wakrah", "Al Khor", "Al Rayyan"],
            "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah"],
            "Saudi Arabia": ["Riyadh", "Jeddah", "Dammam"],
            "Kuwait": ["Kuwait City", "Salmiya", "Hawalli"],
            "Oman": ["Muscat", "Salalah", "Sohar"],
            "Bahrain": ["Manama", "Muharraq"]
        }

        for country_name, cities in data.items():
            country, created = Country.objects.get_or_create(name=country_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Added country: {country_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Country already exists: {country_name}"))

            for city_name in cities:
                city, city_created = City.objects.get_or_create(country=country, name=city_name)
                if city_created:
                    self.stdout.write(self.style.SUCCESS(f"   ↳ Added city: {city_name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"   ↳ City already exists: {city_name}"))

        self.stdout.write(self.style.SUCCESS("\n GCC countries and cities successfully loaded!"))

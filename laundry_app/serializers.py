from rest_framework import serializers
from .models import Service, Country, City, Cart, CartItem, ItemPrice, Item, Order, OrderItem, Laundry, Category

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
        fields = [
            'id',
            'name',
            'country_code',
            'currency_name',
            'currency_code',
            'currency_symbol',
            'cities',
        ]

class LaundrySerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    country_name = serializers.CharField(source='city.country.name', read_only=True)

    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        many=True,
        source="services",
        write_only=True,
        required=False
    )

    services = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Laundry
        fields = [
            'id', 'name',
            'city', 'city_name', 'country_name',
            'address', 'contact_number', 'email',
            'opening_hours', 'rating', 'is_active',
            'services', 'service_ids', 'created_at'
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

class ItemPriceSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_image = serializers.ImageField(source='item.image', read_only=True)

    class Meta:
        model = ItemPrice
        fields = ['id', 'item', 'item_name', 'item_image', 'price']

class ItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'name', 'image', 'price']

    def get_price(self, obj):
        laundry_id = self.context.get("laundry_id")
        try:
            item_price = ItemPrice.objects.get(laundry_id=laundry_id, item=obj)
            return item_price.price
        except ItemPrice.DoesNotExist:
            return None

class CategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'items']

    def get_items(self, obj):
        laundry_id = self.context.get("laundry_id")

        item_prices = ItemPrice.objects.filter(
            laundry_id=laundry_id,
            item__category=obj
        ).select_related("item")

        return [
            {
                "id": ip.item.id,
                "name": ip.item.name,
                "image": ip.item.image.url if ip.item.image else None,
                "price": ip.price,
            }
            for ip in item_prices
        ]



class CartItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    price = serializers.DecimalField(source="service.starting_price", read_only=True,
                                     max_digits=8, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ["id", "service", "service_name", "price", "quantity", "cart"]
        extra_kwargs = {
            "cart": {"write_only": True}
        }

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "laundry", "is_active", "items", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price()

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item_price.item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "item_name", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "laundry", "status", "total_price", "items", "created_at"]
        
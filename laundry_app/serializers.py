from rest_framework import serializers
from .models import (Service, Country, City, Cart, CartItem, ItemPrice, Item, Order, 
    OrderItem, Laundry, Category, CustomerAddress, Language, SupportContact, IssueCategory, ReportedIssue)

GCC_COUNTRIES = [
    "UAE",
    "Saudi Arabia",
    "Qatar",
    "Kuwait",
    "Bahrain",
    "Oman"
]

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"
        read_only_fields = ("user", "created_at")

    def validate_country(self, value):
        if value not in GCC_COUNTRIES:
            raise serializers.ValidationError(
                "Service is available only in GCC countries."
            )
        return value

    def validate(self, data):
        country = data.get("country")

        # Qatar → Zone is mandatory
        if country == "Qatar" and not data.get("zone"):
            raise serializers.ValidationError({
                "zone": "Zone is mandatory for Qatar addresses."
            })

        # UAE → Area is mandatory
        if country == "UAE" and not data.get("area"):
            raise serializers.ValidationError({
                "area": "Area is mandatory for UAE addresses."
            })

        return data

    def create(self, validated_data):
        user = self.context["request"].user

        # Only one default address per user
        if validated_data.get("is_default"):
            CustomerAddress.objects.filter(
                user=user, is_default=True
            ).update(is_default=False)

        validated_data["user"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if validated_data.get("is_default"):
            CustomerAddress.objects.filter(
                user=user, is_default=True
            ).exclude(id=instance.id).update(is_default=False)

        return super().update(instance, validated_data)

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

    services = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Laundry
        fields = [
            'id',
            'name',
            'image',                 
            'city',
            'city_name',
            'country_name',
            'address',
            'contact_number',
            'email',
            'opening_hours',
            'rating',
            'offer_text',            
            'starting_price',        
            'is_active',
            'services',
            'created_at',
        ]


class LaundryCreateSerializer(serializers.ModelSerializer):
    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        many=True,
        source="services",
        required=False
    )

    class Meta:
        model = Laundry
        fields = [
            'id',
            'name',
            'image',              
            'city',
            'address',
            'contact_number',
            'email',
            'opening_hours',
            'rating',
            'offer_text',        
            'starting_price',     
            'is_active',
            'service_ids',
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

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CategoryItemPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPrice
        fields = ["price"]

class ItemWithPriceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "image",
            "price",
        ]

    def get_price(self, obj):
        laundry_id = self.context.get("laundry_id")
        if not laundry_id:
            return None

        price_obj = obj.prices.filter(laundry_id=laundry_id).first()
        return price_obj.price if price_obj else None

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name", "code", "is_rtl"]

class SupportContactSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = SupportContact
        fields = [
            "country",
            "support_phone",
            "support_email"
        ]

    def get_country(self, obj):
        return {
            "id": obj.country.id,
            "name": obj.country.name,
            "country_code": obj.country.country_code,
            "currency_code": obj.country.currency_code,
            "currency_symbol": obj.country.currency_symbol
        }

class IssueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueCategory
        fields = ["id", "title"]


class ReportIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedIssue
        fields = ["id", "issue_category", "custom_issue"]

    def validate(self, data):
        """
        Either issue_category OR custom_issue is required
        """
        if not data.get("issue_category") and not data.get("custom_issue"):
            raise serializers.ValidationError(
                "Please select an issue or write a custom issue."
            )
        return data
        
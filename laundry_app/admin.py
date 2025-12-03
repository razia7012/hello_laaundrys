from django.contrib import admin
from .models import (
    Service, Country, City, Category, Item,
    Laundry, ItemPrice, Cart, CartItem,
    Order, OrderItem
)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "starting_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "country_code", "currency_code", "currency_symbol")
    search_fields = ("name", "country_code")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category__name")


@admin.register(Laundry)
class LaundryAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "contact_number", "rating", "is_active")
    list_filter = ("is_active", "city")
    search_fields = ("name", "city__name")
    filter_horizontal = ("services",)   


@admin.register(ItemPrice)
class ItemPriceAdmin(admin.ModelAdmin):
    list_display = ("item", "laundry", "price")
    list_filter = ("laundry", "item")
    search_fields = ("item__name", "laundry__name")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "laundry", "service", "is_active", "created_at")
    list_filter = ("is_active", "laundry", "service")
    search_fields = ("user__username", "laundry__name")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "laundry", "status", "payment_status", "total_price", "created_at")
    list_filter = ("status", "payment_status", "laundry")
    search_fields = ("user__username", "id")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "item_price", "quantity", "price")
    search_fields = ("order__id", "item_price__item__name")

from django.db import models
from accounts.models import User

ORDER_STATUS = (
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("processing", "Processing"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
)

PAYMENT_STATUS = (
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ("refunded", "Refunded"),
)

class Language(models.Model):
    name = models.CharField(max_length=50)          
    code = models.CharField(max_length=10, unique=True)  
    is_rtl = models.BooleanField(default=False)      
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to="service_images/",
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    starting_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country_code = models.CharField(max_length=5, unique=True)  
    currency_name = models.CharField(max_length=50)             
    currency_code = models.CharField(max_length=10)             
    currency_symbol = models.CharField(max_length=5, blank=True, null=True)  

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.country_code})"


class City(models.Model):
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('country', 'name')
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class Laundry(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="laundry_images/", blank=True, null=True)
    offer_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Eg: 20% OFF on first order"
    )
    starting_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Starting price from"
    )
    city = models.ForeignKey(City, related_name='laundries', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    is_active = models.BooleanField(default=True)
    services = models.ManyToManyField(Service, related_name="laundries")  # ← NEW
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.city.name}"


class ItemPrice(models.Model):
    laundry = models.ForeignKey('Laundry', related_name='item_prices', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='prices', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('laundry', 'item')

    def __str__(self):
        return f"{self.item.name} - {self.price} ({self.laundry.name})"


class Cart(models.Model):
    user = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE)
    laundry = models.ForeignKey('Laundry', related_name='carts', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name='cart_items', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user} for {self.laundry.name}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    item_price = models.ForeignKey(ItemPrice, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'item_price')

    def subtotal(self):
        return self.item_price.price * self.quantity

    def __str__(self):
        return f"{self.item_price.item.name} x {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    laundry = models.ForeignKey(Laundry, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item_price = models.ForeignKey(ItemPrice, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.item_price.item.name} x {self.quantity}"

class CustomerAddress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    name = models.CharField(max_length=100)

    # Optional alternate contact for this address
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Alternate contact number for this address"
    )

    country = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    # GCC flexible address fields
    zone = models.CharField(max_length=10, blank=True)        # Qatar
    area = models.CharField(max_length=100, blank=True)      # UAE / KSA
    street = models.CharField(max_length=100, blank=True)
    building = models.CharField(max_length=100, blank=True)
    apartment = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=10, blank=True)    # Optional (UAE)

    address_line = models.TextField(blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.country} - {self.city}"

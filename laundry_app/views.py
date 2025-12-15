from rest_framework import generics, status
from .models import Service, Country, Cart, CartItem, Laundry, Category
from .serializers import (ServiceSerializer, CountryWithCitiesSerializer, LaundrySerializer, CartSerializer, 
    CartItemSerializer, LaundryCreateSerializer, CategorySerializer, CategoryListSerializer)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .pagination import StandardResultsSetPagination


class ServiceListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer

class LocationListView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = CountryWithCitiesSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'country',  
                openapi.IN_QUERY,  
                description="Filter by country name",
                type=openapi.TYPE_STRING  
            )
        ]
    )

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
    authentication_classes = [TokenAuthentication]
    serializer_class = LaundrySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'city',
            openapi.IN_QUERY,
            description="Filter laundries by city name",
            type=openapi.TYPE_STRING
        )
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        city_name = self.request.query_params.get('city')
        if city_name:
            return Laundry.objects.filter(city__name__icontains=city_name, is_active=True)
        return Laundry.objects.all()

class LaundryCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Laundry.objects.all()
    serializer_class = LaundryCreateSerializer
    permission_classes = [IsAuthenticated]

class AddToCartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        laundry_id = request.data.get("laundry")
        service_id = request.data.get("service")
        quantity = int(request.data.get("quantity", 1))

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)

        cart, created = Cart.objects.get_or_create(
            user=user,
            laundry_id=laundry_id,
            is_active=True
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            service=service,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({
            "message": "Item added to cart",
            "cart": CartSerializer(cart).data
        })

class LaundryItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, laundry_id):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True, context={"laundry_id": laundry_id})
        return Response(serializer.data)

class PlaceOrderView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user, is_active=True)
        except Cart.DoesNotExist:
            return Response({"error": "No active cart found"}, status=400)

        order = Order.objects.create(
            user=user,
            laundry=cart.laundry,
            status="pending",
            payment_status="pending"
        )

        total = 0

        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                item_price=cart_item.item_price,
                quantity=cart_item.quantity,
                price=cart_item.item_price.price
            )
            total += order_item.subtotal()

        order.total_price = total
        order.save()

        cart.is_active = False
        cart.save()

        return Response({
            "message": "Order placed successfully",
            "order_id": order.id
        }, status=201)

class UpdateOrderStatusView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        status_to_update = request.data.get("status")

        if status_to_update not in dict(ORDER_STATUS):
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.status = status_to_update
        order.save()

        return Response({"message": "Order status updated"})


class UpdatePaymentStatusView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        new_status = request.data.get("payment_status")

        if new_status not in dict(PAYMENT_STATUS):
            return Response({"error": "Invalid payment status"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.payment_status = new_status
        order.save()

        return Response({"message": "Payment status updated successfully"})


class CategoryListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer

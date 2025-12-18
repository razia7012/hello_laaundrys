from rest_framework import generics, status
from .models import Service, Country, Cart, CartItem, Laundry, Category, CustomerAddress, Language, SupportContact, IssueCategory, LaundryReview, Laundry
from .serializers import (ServiceSerializer, CountryWithCitiesSerializer, LaundrySerializer, CartSerializer, 
    CartItemSerializer, LaundryCreateSerializer, CategorySerializer, CategoryListSerializer, ItemWithPriceSerializer, CustomerAddressSerializer,
    LanguageSerializer, SupportContactSerializer, IssueCategorySerializer, ReportIssueSerializer, LaundryReviewSerializer)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .pagination import StandardResultsSetPagination

class LanguageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = LanguageSerializer

    def get_queryset(self):
        return Language.objects.filter(is_active=True)

class CustomerAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomerAddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return CustomerAddress.objects.none()
        return CustomerAddress.objects.filter(user=user)

class CustomerAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerAddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return CustomerAddress.objects.none()
        return CustomerAddress.objects.filter(user=user)

class SetDefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, pk):
        try:
            address = CustomerAddress.objects.get(
                pk=pk, user=request.user
            )
        except CustomerAddress.DoesNotExist:
            return Response(
                {"detail": "Address not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        CustomerAddress.objects.filter(
            user=request.user, is_default=True
        ).update(is_default=False)

        address.is_default = True
        address.save()

        return Response(
            {"message": "Default address set successfully"}
        )

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
    permission_classes = [IsAuthenticated]
    serializer_class = LaundrySerializer
    pagination_class = StandardResultsSetPagination

    queryset = Laundry.objects.filter(is_active=True)

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = {
        'city__name': ['icontains'],
        'rating': ['gte', 'lte'],
        'starting_price': ['gte', 'lte'],
    }

    ordering_fields = [
        'rating',
        'starting_price',
        'created_at',
        'name'
    ]

    ordering = ['-created_at']  

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('city__name', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="City name"),
            openapi.Parameter('rating__gte', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Min rating"),
            openapi.Parameter('rating__lte', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Max rating"),
            openapi.Parameter('starting_price__gte', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Min price"),
            openapi.Parameter('starting_price__lte', openapi.IN_QUERY, type=openapi.TYPE_NUMBER, description="Max price"),
            openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Sort by: rating, -rating, starting_price, -created_at"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class LaundryCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Laundry.objects.all()
    serializer_class = LaundryCreateSerializer

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
    authentication_classes = [TokenAuthentication]

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

class ItemsByCategoryWithPriceView(generics.ListAPIView):
    serializer_class = ItemWithPriceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "category_id",
                openapi.IN_QUERY,
                description="Category ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "category_name",
                openapi.IN_QUERY,
                description="Category name (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "laundry_id",
                openapi.IN_QUERY,
                description="Laundry ID to fetch item prices",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.query_params.get("category_id")
        category_name = self.request.query_params.get("category_name")

        queryset = Item.objects.all()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        elif category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        else:
            return Item.objects.none()

        return queryset.prefetch_related("prices")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["laundry_id"] = self.request.query_params.get("laundry_id")
        return context

class SupportContactView(APIView):
    """
    Get support contact based on country NAME
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "country_name",
                openapi.IN_QUERY,
                description="Country name (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ]
    )
    def get(self, request):
        country_name = request.query_params.get("country")

        if not country_name:
            return Response(
                {"message": "country parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            support = SupportContact.objects.select_related("country").get(
                country__name__iexact=country_name,
                is_active=True
            )
        except SupportContact.DoesNotExist:
            return Response(
                {"message": "Support contact not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupportContactSerializer(support)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IssueCategoryListView(APIView):
    """
    List predefined issues
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        issues = IssueCategory.objects.filter(is_active=True)
        serializer = IssueCategorySerializer(issues, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class ReportIssueView(APIView):
    """
    Report an issue (select or custom)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReportIssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response({
                "success": True,
                "message": "Issue reported successfully"
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LaundryReviewListView(APIView):
    """
    List all reviews for a laundry
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'laundry_id',
                openapi.IN_PATH,
                description="Laundry ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: LaundryReviewSerializer(many=True)}
    )
    def get(self, request, laundry_id):
        reviews = LaundryReview.objects.filter(laundry_id=laundry_id)
        serializer = LaundryReviewSerializer(reviews, many=True)
        return Response({"success": True, "data": serializer.data})


class LaundryReviewCreateView(APIView):
    """
    Add a new review for a laundry
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, laundry_id):
        data = request.data.copy()
        data['customer'] = request.user.id
        data['laundry'] = laundry_id
        serializer = LaundryReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Review added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

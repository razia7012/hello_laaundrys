from django.urls import path
from . import views

urlpatterns = [
 path('services/', views.ServiceListAPIView.as_view(), name='service-list'),
 path('locations/', views.LocationListView.as_view(), name='locations'),
 path('laundries/', views.LaundryListByCityView.as_view(), name='laundry-list-by-city'),
 path('categories/', views.CategoryListView.as_view(), name='category-list'),
 path('create-laundry/', views.LaundryCreateView.as_view(), name='create-laundry'),
 path("add/", views.AddToCartView.as_view(), name="add-to-cart"),
 path('laundry/<int:laundry_id>/items/', views.LaundryItemListView.as_view(), name='laundry-items'),
 path('order/place/', views.PlaceOrderView.as_view(), name='place-order'),
 path('order/<int:order_id>/status/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
 path('order/<int:order_id>/payment-status/', views.UpdatePaymentStatusView.as_view(), name='update-payment-status'),
]

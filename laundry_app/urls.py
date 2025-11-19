from django.urls import path
from .views import as laundry_app_views

urlpatterns = [
 path('services/', laundry_app_views.ServiceListAPIView.as_view(), name='service-list'),
 path('locations/', laundry_app_views.LocationListView.as_view(), name='locations'),
 path('laundries/', laundry_app_views.LaundryListByCityView.as_view(), name='laundry-list-by-city'),
 path('laundries/', LaundryCreateView.as_view(), name='create-laundry'),
 path("add/", laundry_app_views.AddToCartView.as_view(), name="add-to-cart"),
 path('laundry/<int:laundry_id>/items/', laundry_app_views.LaundryItemListView.as_view(), name='laundry-items'),
 path('order/place/', laundry_app_views.PlaceOrderView.as_view(), name='place-order'),
 path('order/<int:order_id>/status/', laundry_app_views.UpdateOrderStatusView.as_view(), name='update-order-status'),
 path('order/<int:order_id>/payment-status/', laundry_app_views.UpdatePaymentStatusView.as_view(), name='update-payment-status'),

]

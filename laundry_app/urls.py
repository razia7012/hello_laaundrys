from django.urls import path
from . import views

urlpatterns = [
 path('services/', views.ServiceListAPIView.as_view(), name='service-list'),
 path('locations/', views.LocationListView.as_view(), name='locations'),
 path('laundries/', views.LaundryListByCityView.as_view(), name='laundry-list-by-city'),
 path('laundries/create/', views.LaundryCreateView.as_view(), name='create-laundry'),
 path('laundries/<int:laundry_id>/items/', views.LaundryItemListView.as_view(), name='laundry-items'),
 path("laundries/<int:laundry_id>/reviews/", views.LaundryReviewListView.as_view(), name="laundry-reviews-list"),
 path("laundries/<int:laundry_id>/reviews/add/", views.LaundryReviewCreateView.as_view(), name="laundry-reviews-add"),
 path('categories/', views.CategoryListView.as_view(), name='category-list'),
 path('add/', views.AddToCartView.as_view(), name="add-to-cart"),
 path('order/place/', views.PlaceOrderView.as_view(), name='place-order'),
 path('order/<int:order_id>/status/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
 path('order/<int:order_id>/payment-status/', views.UpdatePaymentStatusView.as_view(), name='update-payment-status'),
 path('items/by-category/', views.ItemsByCategoryWithPriceView.as_view(), name="items-by-category-with-price"),
 path('customer/addresses', views.CustomerAddressListCreateView.as_view(), name="address-list"),
 path('customer/addresses/<int:pk>', views.CustomerAddressDetailView.as_view(), name="address-details"),
 path('customer/addresses/<int:pk>/set-default', views.SetDefaultAddressView.as_view(), name="set-default"),
 path('languages/', views.LanguageListView.as_view(), name="language-list"),
 path("support-contact/", views.SupportContactView.as_view(), name="support-contact"),
 path("issues/", views.IssueCategoryListView.as_view(), name="issue-list"),
 path("issues/report/", views.ReportIssueView.as_view(), name="report-issue"),
 
 
]

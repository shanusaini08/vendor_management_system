from django.urls import path
from apis import views

urlpatterns = [

    ####################### Auth #######################

    path('login/', views.LoginView.as_view(), name='login'),

    ####################### Buyer CRUD  #######################

    path('buyers/signup/', views.BuyerSignupView.as_view(), name='buyer_signup'),
    path('buyers/by_id/', views.BuyerProfileView.as_view(), name='buyer_view'),
    path('buyers/', views.BuyerListView.as_view(), name='buyer_list'),

    ####################### Buyer Purchase Order #######################

    path('buyers/purchase_orders/', views.PurchaseOrderCreateAPIView.as_view(), name='buyer_purchase_orders'),
    path('buyers/purchase_orders/cancel/<int:purchase_order_id>/', views.CancelPurchaseOrderView.as_view(), name='cancel_purchase_order'),
    path('buyers/purchase_orders/rate/<int:purchase_order_id>/', views.RatePurchaseOrderView.as_view(), name='rate_purchase_order'),


    ####################### Vendor CRUD  #######################

    path('vendors/signup/', views.VendorSignupView.as_view(), name='vendor_signup'),
    path('vendors/by_id/', views.VendorDetailView.as_view(), name='vendor-detail'),
    path('vendors/', views.VendorView.as_view(), name='vendors'),

    ####################### Vendor Items  #######################

    path('vendors/items/', views.ItemCreateAPIView.as_view(), name='items'),
    path('vendors/items/update', views.ItemUpdateView.as_view(), name='items-update'),
    path('vendors/items/delete/<int:item_id>/', views.ItemDeleteView.as_view(), name='delete-item'),

    ####################### Vendor Purchase Order #######################

    path('vendors/orders/', views.PurchaseOrderListView.as_view(), name='items'),
    path('vendors/purchase_orders/<int:purchase_order_id>/issue/', views.IssuePurchaseOrderView.as_view(), name='issue_purchase_order'),
    path('vendors/purchase_orders/<int:purchase_order_id>/acknowledge/', views.AcknowledgePurchaseOrderView.as_view(), name='acknowledge_purchase_order'),
    path('vendors/purchase_orders/<int:purchase_order_id>/complete/', views.CompletePurchaseOrderView.as_view(), name='complete_purchase_order'),

    ####################### Vendor Performance #######################

    path('vendors/performance/', views.PerformanceMetricsAPIView.as_view(), name='vendor_performance'),
    path('vendors/historical-performance/', views.VendorHistoricalPerformance.as_view(), name='vendor-historical-performance'),

]

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/overview', views.dashboard_overview),
    path('transactions', views.create_transaction),
    path('transactions/suspicious', views.suspicious_transactions),
    path('inventory/low-stock', views.low_stock_products),
    #path('analytics/hourly-sales', views.hourly_sales), #commencted the old endpoint
    path('analytics/sales-over-time', views.sales_over_time),  
    path('analytics/top-products', views.top_products),
    path('alerts', views.create_alert),
]
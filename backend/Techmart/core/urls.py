from django.urls import path
from . import views

#Defining the URL Patterns specific to the app
urlpatterns = [
    path('dashboard/overview', views.dashboard_overview),
    path('transactions', views.create_transaction),
    path('transactions/suspicious', views.suspicious_transactions),
    path('inventory/low-stock', views.low_stock_products),
    path('analytics/hourly-sales', views.hourly_sales),
    path('alerts', views.create_alert),
]
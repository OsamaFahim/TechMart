#from django.shortcuts import render

# Create your views here.
from django.db import transaction  # TO make create transaction function atomic
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import Product, Transaction, Customer
from .serializers import TransactionSerializer, ProductSerializer
from datetime import timedelta
from django.utils.dateparse import parse_date
from decimal import Decimal

# Helper: Calculate risk score 
def calculate_risk_score(customer):
    # Get recent transactions for the customer in the last 30 days
    recent_transactions = Transaction.objects.filter(customer=customer, timestamp__gte=timezone.now()-timedelta(days=30))
    aggregated_data = recent_transactions.aggregate(Sum('total_amount'))
    # total_spent is a Decimal or None
    total_spent = aggregated_data['total_amount__sum'] or Decimal("0")
    count = recent_transactions.count()
    # Example: high spenders or frequent buyers are higher risk
    # Ensures that score never exceeds 1.0 (100% )
    # if user spends 10,000$ or more and do more than 50 transactions then this part becomes >= 1 and
    # then we take the minimum
    # FIX: Use Decimal for all calculations to avoid Decimal/float error
    risk_score = total_spent / Decimal("10000") + Decimal(str(count)) / Decimal("50")
    return float(min(Decimal("1.0"), risk_score))

# 1. Dashboard Overview
@api_view(['GET'])
def dashboard_overview(request):
    # Cache dashboard stats for 1 minute, as they are expensive and frequently accessed
    cache_key = "dashboard_overview"
    data = cache.get(cache_key)
    if data:
        return Response(data)
    
    now = timezone.now()
    since = now - timedelta(hours=24)
    sales_aggregate = Transaction.objects.filter(timestamp__gte=since).aggregate(Sum('total_amount'))
    total_sales = sales_aggregate['total_amount__sum'] or 0
    total_transactions = Transaction.objects.filter(timestamp__gte=since).count()
    new_customers = Customer.objects.filter(registration_date__gte=since.date()).count()
    low_stock = Product.objects.filter(stock_quantity__lt=10).count()

    result = {
        "total_sales": total_sales,
        "total_transactions": total_transactions,
        "new_customers": new_customers,
        "low_stock_products": low_stock
    }
    cache.set(cache_key, result, timeout=60)
    return Response(result)

# 2. Create Transaction
@api_view(['POST'])
def create_transaction(request):
    from decimal import Decimal, InvalidOperation

    try:
        with transaction.atomic():
            data = request.data
            try:
                amount = Decimal(str(data.get('total_amount', "0")))
            except (InvalidOperation, TypeError):
                return Response({"error": "Invalid total_amount format."}, status=status.HTTP_400_BAD_REQUEST)

            if not (Decimal("0.01") <= amount <= Decimal("10000")):
                return Response({"error": "Amount must be between $0.01 and $10,000."}, status=status.HTTP_400_BAD_REQUEST)
            
            product = Product.objects.get(id=data['product'])
            try:
                quantity = int(data['quantity'])
            except (ValueError, TypeError):
                return Response({"error": "Invalid quantity format."}, status=status.HTTP_400_BAD_REQUEST)

            if product.stock_quantity < quantity:
                return Response({"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = TransactionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                product.stock_quantity -= quantity
                product.save()
                customer = Customer.objects.get(id=data['customer'])
                customer.risk_score = calculate_risk_score(customer)
                customer.save()
                # Invalidate all relevant caches so new data is fetched
                cache.delete("dashboard_overview")
                cache.delete("top_products")
                cache.delete_pattern("low_stock_products*")
                cache.delete_pattern("sales_over_time*")
                cache.delete_pattern("suspicious_transactions*")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 3. Suspicious Transactions
@api_view(['GET'])
def suspicious_transactions(request):
    # Cache suspicious transactions for 30 seconds
    cache_key = "suspicious_transactions"
    data = cache.get(cache_key)
    if data:
        return Response(data)
    suspicious = Transaction.objects.filter(
        Q(total_amount__gt=5000) | Q(total_amount__lt=1) |
        Q(timestamp__gte=timezone.now()-timedelta(minutes=1))
    )
    serializer = TransactionSerializer(suspicious, many=True)
    cache.set(cache_key, serializer.data, timeout=30)
    return Response(serializer.data)

# 4. Low Stock Products
@api_view(['GET'])
def low_stock_products(request):
    threshold = int(request.GET.get('threshold', 10))
    cache_key = f"low_stock_products_{threshold}"
    data = cache.get(cache_key)
    if data:
        return Response(data)
    products = Product.objects.filter(stock_quantity__lt=threshold)
    serializer = ProductSerializer(products, many=True)
    cache.set(cache_key, serializer.data, timeout=60)
    return Response(serializer.data)

# 5. Create Alert
@api_view(['POST'])
def create_alert(request):
    alert = request.data.get('alert')
    if not alert:
        return Response({"error": "Alert message required."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Alert created", "alert": alert}, status=status.HTTP_201_CREATED)

#6. Sales over Time (Hourly or according to date ranges)
@api_view(['GET'])
def sales_over_time(request):
    date_from = request.GET.get('dateFrom')
    date_to = request.GET.get('dateTo')
    category = request.GET.get('category')
    segment = request.GET.get('segment')
    cache_key = f"sales_over_time_{date_from}_{date_to}_{category}_{segment}"
    data = cache.get(cache_key)
    if data:
        return Response(data)

    qs = Transaction.objects.all()
    if date_from:
        qs = qs.filter(timestamp__date__gte=parse_date(date_from))
    if date_to:
        qs = qs.filter(timestamp__date__lte=parse_date(date_to))
    if category and category != "All":
        qs = qs.filter(product__category=category)
    if segment and segment != "All":
        qs = qs.filter(customer__loyalty_tier=segment)

    sales_by_date = (
        qs.extra({'date': "date(timestamp)"})
        .values('date')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('date')
    )
    result = list(sales_by_date)
    cache.set(cache_key, result, timeout=60)
    return Response(result)

#. Top products
@api_view(['GET'])
def top_products(request):
    cache_key = "top_products"
    data = cache.get(cache_key)
    if data:
        return Response(data)
    top_products = (
        Transaction.objects
        .values('product', 'product__name', 'product__category')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:10]
    )
    result = []
    for prod in top_products:
        prod['id'] = prod['product']
        result.append(prod)
    cache.set(cache_key, result, timeout=60)
    return Response(result)

#Previous endpoint, it was grouping by hour and not the day, it was always showing zero so 
#i created a new endpoint which takes date ranges as parameters
"""
# 5. Hourly Sales Analytics
@api_view(['GET'])
def hourly_sales(request):
    now = timezone.now()
    #with the last 24 hours
    since = now - timedelta(hours=24)
    #gets sales within the last 24 hours
    sales = Transaction.objects.filter(timestamp__gte=since)
    hourly_data = []
    for hour in range(24):
        #Defining start of the hour window
        start = since + timedelta(hours=hour)

        #Defining the end of the hour window (1 hour after start) (start + 1)
        end = start + timedelta(hours=1)
        
        # Filter transactions within this 1-hour window
        hourly_sales_qs = sales.filter(timestamp__gte=start, timestamp__lt=end)

        # Sum up their total_amount
        aggregate_result = hourly_sales_qs.aggregate(Sum('total_amount')) #return dictionary
        #total_amount_sum is key value
        total = aggregate_result['total_amount__sum'] or 0  # if None, fallback to 0

        #Fommrat hour and append to list
        hourly_data.append({"hour": start.strftime("%H:00"), 
                            "total_sales": total})
    return Response(hourly_data)
"""
#from django.shortcuts import render

# Create your views here.
from django.db import transaction  # TO make create transaction function atomic
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

# Helper: Calculate risk score (simple example)
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
#This is a GET API point
@api_view(['GET'])
def dashboard_overview(request):
    now = timezone.now()
    #This calculates exactly 24 hours ago
    since = now - timedelta(hours=24)

    #gte => greater than or equal to (Django QuerySet field loopups)

    #get all the the transactions in the last 24 hours, and add up total_amount (transaction field)
    #using the aggregare function, so it sums the toal amount using the aggregate SUM()
    sales_aggregate = Transaction.objects.filter(timestamp__gte=since).aggregate(Sum('total_amount'))
    #Sales aggreagte stores a dictionary like {'total_amount__sum' : SUM like 4000} so we fetch the 
    #total sales from the dictionary and total_amount__sum is name automatically given by Django
    #to key of the Dictionary.
    total_sales = sales_aggregate['total_amount__sum'] or 0


    #total transactions in last 24 houts 
    total_transactions = Transaction.objects.filter(timestamp__gte=since).count()
    #.date only fileters the date and not the time
    #new customers who registered within the past 24 hours
    new_customers = Customer.objects.filter(registration_date__gte=since.date()).count()
    #le is less than
    #Finding all numbers where stock quantity is less than 10
    low_stock = Product.objects.filter(stock_quantity__lt=10).count()

    return Response({
        "total_sales": total_sales,
        "total_transactions": total_transactions,
        "new_customers": new_customers,
        "low_stock_products": low_stock
    })

# 2. Create Transaction
# POST API ENDPOINT To create a transaction
@api_view(['POST'])
def create_transaction(request):
    from decimal import Decimal, InvalidOperation

    try:
        with transaction.atomic():  # Ensures all DB operations are atomic
            data = request.data
            # Validate amount (Handled business validation of reasonable Amount)
            # Data is usually a dictionary, so it tries to get total_amount from data else 0
            try:
                amount = Decimal(str(data.get('total_amount', "0")))
            except (InvalidOperation, TypeError):
                return Response({"error": "Invalid total_amount format."}, status=status.HTTP_400_BAD_REQUEST)

            if not (Decimal("0.01") <= amount <= Decimal("10000")):
                return Response({"error": "Amount must be between $0.01 and $10,000."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate product and stock
            # We send the id of the product that we bought and check stock_quantity of that product
            # that if we are not over buying than what is present in stock
            product = Product.objects.get(id=data['product'])
            try:
                quantity = int(data['quantity'])
            except (ValueError, TypeError):
                return Response({"error": "Invalid quantity format."}, status=status.HTTP_400_BAD_REQUEST)

            if product.stock_quantity < quantity:
                return Response({"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save transaction
            # Deserialize (convert) the input data and prepare it for validation
            serializer = TransactionSerializer(data=data)
            if serializer.is_valid():
                # It runs custom validations, handling nested objects and handle some complex scenarios
                serializer.save()
                # Update stock
                product.stock_quantity -= quantity
                product.save()
                
                # Update customer risk score
                customer = Customer.objects.get(id=data['customer'])
                customer.risk_score = calculate_risk_score(customer)
                customer.save()
                # Return successful response
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Added: If Decimal/float mix error occurs, this will catch and show a clear message
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 3. Suspicious Transactions
@api_view(['GET'])
def suspicious_transactions(request):
    # Example: Unusual amounts or rapid purchases (within 1 min)
    suspicious = Transaction.objects.filter(
        Q(total_amount__gt=5000) | Q(total_amount__lt=1) |
        Q(timestamp__gte=timezone.now()-timedelta(minutes=1))
    )
    serializer = TransactionSerializer(suspicious, many=True)
    return Response(serializer.data)

# 4. Low Stock Products
@api_view(['GET'])
def low_stock_products(request):
    #gets threshold from the request and makes threshold = 10
    threshold = int(request.GET.get('threshold', 10))

    #gets products whose stock quantity is less than (lt) threhold
    products = Product.objects.filter(stock_quantity__lt=threshold)

    #many tells, we are serializing a list and not a single object
    #we are using our implementation of Product serializer to convert query sets to lists
    #so that we can covert to json and return
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# 5. Create Alert
@api_view(['POST'])
def create_alert(request):
    # In real app, save to DB or send notification
    alert = request.data.get('alert')
    if not alert:
        return Response({"error": "Alert message required."}, status=status.HTTP_400_BAD_REQUEST)
    # Here, just echo back for demo
    return Response({"message": "Alert created", "alert": alert}, status=status.HTTP_201_CREATED)

#6. Sales over Time (Hourly or according to date ranges)
@api_view(['GET'])
def sales_over_time(request):
    #These are the send along with the request
    date_from = request.GET.get('dateFrom')
    date_to = request.GET.get('dateTo')
    category = request.GET.get('category')
    segment = request.GET.get('segment')

    #storing all the objects of Transactions in qs
    qs = Transaction.objects.all()

    #Converting date from into proper python objects    
    if date_from:
        #filters transactions on or after start date from by gte(greater than equal)
        qs = qs.filter(timestamp__date__gte=parse_date(date_from))
    if date_to:
        #filters transactions on or before due date from by lte(less than equal)
        qs = qs.filter(timestamp__date__lte=parse_date(date_to))

    if category and category != "All":
        qs = qs.filter(product__category=category)
    if segment and segment != "All":
        qs = qs.filter(customer__loyalty_tier=segment)

    # Group by date
    sales_by_date = (
        qs.extra({'date': "date(timestamp)"})
        .values('date')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('date')
    )

    #Returning sles data as a list
    return Response(list(sales_by_date))

#. Top products
@api_view(['GET'])
def top_products(request):
    # Aggregate total quantity sold for each product, include name and category
    top_products = (
        Transaction.objects
        .values('product', 'product__name', 'product__category')
        .annotate(total_sold=Sum('quantity'))
        #add up the quatity values for these products
        .order_by('-total_sold')[:10]  # Top 10 products
    )
    # Add product id as 'id' for frontend DataGrid compatibility
    for prod in top_products:
        prod['id'] = prod['product']
    return Response(list(top_products))

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

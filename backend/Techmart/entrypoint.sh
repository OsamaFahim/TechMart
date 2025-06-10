#!/usr/bin/env bash

set -e
# Waitingfor the DB to be ready and run migrations
./wait-for-it.sh db 3306 --timeout=60 --strict -- python manage.py migrate

# Running the data loader if key tables are empty
echo "Checking if key tables are empty..."
# Checking counts of key tables
SUPPLIER_COUNT=$(python manage.py shell -c "from core.models import Supplier; print(Supplier.objects.count())" | tail -n 1 | tr -d '[:space:]')
PRODUCT_COUNT=$(python manage.py shell -c "from core.models import Product; print(Product.objects.count())" | tail -n 1 | tr -d '[:space:]')
CUSTOMER_COUNT=$(python manage.py shell -c "from core.models import Customer; print(Customer.objects.count())" | tail -n 1 | tr -d '[:space:]')
TRANSACTION_COUNT=$(python manage.py shell -c "from core.models import Transaction; print(Transaction.objects.count())" | tail -n 1 | tr -d '[:space:]')

#if the count of all tables is zero, we run the data loader because it means no data has been loaded yet and db is empty
if [ "$SUPPLIER_COUNT" = "0" ] && [ "$PRODUCT_COUNT" = "0" ] && [ "$CUSTOMER_COUNT" = "0" ] && [ "$TRANSACTION_COUNT" = "0" ]; then
    echo "All key tables are empty. Running data loader..."
    python manage.py load
else
    echo "Some data already exists. Skipping data loader."
fi

# starting Gunicorn after migrations succeed
gunicorn Techmart.wsgi:application --bind 0.0.0.0:8000
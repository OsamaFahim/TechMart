from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    #I noticed that some phone number were also null, so allow nulls here
    phone = models.CharField(max_length=50, null = True, blank=True)
    address = models.TextField()
    country = models.CharField(max_length=100)
    reliability_score = models.FloatField()
    average_delivery_days = models.IntegerField()
    payment_terms = models.CharField(max_length=255)
    established_date = models.DateField()
    #I noticed that some certications are null, so we are allowing null here
    certification = models.CharField(max_length=255, null = True, blank = True)

    #So that the Supplier method instance attributes to return a meaningful 
    #string which represnets the specific entity for eg here it will be
    #represented by the name
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    sku = models.CharField(max_length=100)
    description = models.TextField(null = True, blank = True)
    weight = models.FloatField()
    dimensions = models.CharField(max_length=255)
    #some warranty months were also null, so I am allowing null here as well
    warranty_months = models.IntegerField(null = True, blank = True)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.name
    
    class Meta:
        #Creating indexes on caetrogry and supplier, as they have been used by our queries in
        #views.py
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['supplier']),
        ]

class Customer(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    registration_date = models.DateField()
    total_spent = models.DecimalField(max_digits=12, decimal_places=2)
    risk_score = models.FloatField()
    address = models.TextField()
    #some phone numbers were also null, so I am allowing null here as well
    phone = models.CharField(max_length=50, null = True, blank = True)
    date_of_birth = models.DateField()
    preferred_payment = models.CharField(max_length=100)
    loyalty_tier = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

#In the transactions table, everything is a must and no column is emoty, it is the table with
#most number of rows
class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    session_id = models.CharField(max_length=255)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction #{self.id} - {self.customer}"
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['customer']),
            models.Index(fields=['product']),
            models.Index(fields=['total_amount']),
        ]

from rest_framework import serializers
from .models import Supplier, Product, Customer, Transaction

"""
    Defining Serializers for four methods, so that complex data types like 
    Django models, querysets, are converted into native Python datatypes
    so we can convert them to json and communicate with the frontend
"""


#Model serializer helps us in not manually declaring every field
#It helps follow DRY principle
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        #It would be like field = ['name', 'price'] etc

#Similarly for other Serializers, same concept is being followed 
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
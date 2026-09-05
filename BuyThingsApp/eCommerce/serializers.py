from rest_framework import serializers
from .models import Store, Product, Review
from django.contrib.auth.models import User

      
class ProductSerializer(serializers.ModelSerializer):
    """Serializes a Product's core fields, without its reviews."""

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'store']
        

class StorePostSerializer(serializers.ModelSerializer):
    """Serializes a Store's core fields for creating a store via the API."""

    class Meta:
        model = Store
        fields = ['vendor', 'name', 'description']       

class StoreSerializer(serializers.ModelSerializer):
    """Serializes a Store along with its associated products (read-only)."""

    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Store
        fields = ['vendor', 'name', 'description', 'products']
 
 
class ReviewSerializer(serializers.ModelSerializer):
    """Serializes a Review's core fields."""

    class Meta:
        model = Review
        fields = ['title', 'body', 'product', 'author', 'verified']
        
        
class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializes a Product along with its associated reviews (read-only)."""

    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'store', 'reviews']

      
class StoreReviewSerializer(serializers.ModelSerializer):
    """Serializes a Store along with its products and each product's reviews (read-only)."""

    products = ProductReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Store
        fields = ['vendor', 'name', 'description', 'products']


class VendorSerializer(serializers.ModelSerializer):
    """Serializes a vendor (User) along with the stores they own (read-only)."""

    stores = StoreSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'stores']

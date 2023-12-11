from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'category', 'title', 'price', 'category_id', 'featured']
        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'groups', 'user_permissions']
        depth = 3
        
class CartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'user_id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        depth = 5
        
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    delivery_user = UserSerializer(read_only=True)
    delivery_user_id = serializers.IntegerField(write_only=True)
    
    status = serializers.BooleanField(read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2)
    date = serializers.DateField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['user', 'delivery_user', 'delivery_user_id', 'status', 'total', 'date']
        
class OrderItemSerializer(serializers.ModelSerializer):
    
    # TODO Look at Admin panel for proper fields to implement
    # TODO It'll actually all be read only since when a new order is created,
    # for each cart item by menuitem_id, a new order item will be created.
    # so all here is read only lol. You'll have to do the data transfer logic in the view
    
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
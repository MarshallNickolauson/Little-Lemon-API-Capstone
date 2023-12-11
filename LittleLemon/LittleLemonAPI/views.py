from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth.models import User, Group
from rest_framework.decorators import action

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
    
class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='DeliveryCrew').exists()

class MenuItemView(ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        elif self.action == 'list':
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
class ManagerGroupView(ModelViewSet):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [IsManager]
    
    @action(detail=False, methods=['post'])
    def assign_to_manager_group(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        manager_group = Group.objects.get(name='Manager')
        user.groups.add(manager_group)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, 201, headers=headers)
    
    @action(detail=False, methods=['delete'])
    def remove_manager_role(self, request, pk=None):
        try:
            user = self.get_object()
            manager_group = Group.objects.get(name='Manager')
            
            if manager_group in user.groups.all():
                user.groups.remove(manager_group)
                serializer = self.get_serializer(user)
                return Response(serializer.data, 200)
            else:
                return Response('User does not have Manager role.', 400)
        except User.DoesNotExist:
            return Response({'User not found.', 404})
        
class DeliveryCrewGroupView(ModelViewSet):
    queryset = User.objects.filter(groups__name='DeliveryCrew')
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    @action(detail=False, methods=['post'])
    def assign_to_deliver_crew_group(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        delivery_crew_group = Group.objects.get(name='DeliveryCrew')
        user.groups.add(delivery_crew_group)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, 201, headers=headers)

    @action(detail=False, methods=['delete'])
    def remove_delivery_crew_role(self, request, pk=None):
        try:
            user = self.get_object()
            delivery_crew_group = Group.objects.get(name='DeliveryCrew')
            
            if delivery_crew_group in user.groups.all():
                user.groups.remove(delivery_crew_group)
                serializer = self.get_serializer(user)
                return Response(serializer.data, 200)
            else:
                return Response('User does not have Delivery Crew role.', 400)
        except User.DoesNotExist:
            return Response({'User not found.', 404})
    
class CartView(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user_id'] = self.request.user.id
        
        menuitem_id = data['menuitem_id']
        if menuitem_id:
            try:
                MenuItem.objects.get(pk=menuitem_id)
            except MenuItem.DoesNotExist:
                return Response({'Invalid menuitem_id'}, 400)
            
        existing_cart_entry = Cart.objects.filter(user=self.request.user, menuitem_id=menuitem_id).first()
                 
        if existing_cart_entry:
            existing_cart_entry.quantity += int(data.get('quantity', 1))
            existing_cart_entry.save()
            cart_serializer = self.get_serializer(existing_cart_entry)
            return Response(cart_serializer.data, 200)
        else:
            cart_serializer = self.get_serializer(data=data)
            cart_serializer.is_valid(raise_exception=True)
            cart_serializer.save()
            return Response(cart_serializer.data, 200)
        
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response('All cart items deleted successfully.', 200)
    
class OrderView(ModelViewSet):
    # TODO Look at Order Model
    pass

class OrderItemView(ModelViewSet):
    pass
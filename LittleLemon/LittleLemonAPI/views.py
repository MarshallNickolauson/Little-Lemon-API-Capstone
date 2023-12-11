from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth.models import User, Group
from rest_framework.decorators import action

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
    
class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='DeliveryCrew').exists()

class MenuItemView(ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        elif self.action == 'list':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
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
    queryset = User.objects.filter(groups__name='DeliveryCrew')
    serializer_class = UserSerializer
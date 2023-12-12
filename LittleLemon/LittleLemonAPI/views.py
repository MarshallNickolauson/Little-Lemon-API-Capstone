from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth.models import User, Group
from rest_framework.decorators import action
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage

from .models import *
from .serializers import *

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
    
    def list(self, request, *args, **kwargs):
        
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        page = request.query_params.get('page', default=1)
        perpage = request.query_params.get('perpage', default=2)
        
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
            
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
            
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data, 200)
    
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
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
        
    def list(self, request, *args, **kwargs):
        try:            
            user = self.request.user
            orders = Order.objects.none()
            order_items = OrderItem.objects.none()

            if IsManager.has_permission(self, request, self):
                orders = Order.objects.all()
                order_items = OrderItem.objects.select_related('order').all()
            elif IsDeliveryCrew.has_permission(self, request, self):
                orders = Order.objects.filter(status=0)
                order_items = OrderItem.objects.filter(order__in=orders)
            else:
                orders = Order.objects.filter(user=user)
                order_items = OrderItem.objects.filter(order__in=orders)
                
            status_filter = request.query_params.get('status')
            if status_filter is not None:
                orders = orders.filter(status=status_filter)
            
            ordering = request.query_params.get('ordering')
            if ordering:
                ordering_fields = ordering.split(",")
                orders = orders.order_by(*ordering_fields)
                
            page = request.query_params.get('page', default=1)
            perpage = request.query_params.get('perpage', default=2)
            paginator = Paginator(orders, per_page=perpage)
            try:
                orders = paginator.page(number=page)
            except EmptyPage:
                orders = []
            
            order_serializer = OrderSerializer(orders, many=True)
            order_items_serializer = OrderItemSerializer(order_items, many=True)

            response_data = {
                'orders': order_serializer.data,
                'order_items': order_items_serializer.data,
            }

            return Response(response_data, 200)

        except Exception as e:
            print(e)
            return Response({'error':str(e)}, 500)
        
    @action(detail=True, methods=['get'])
    def list_order_with_items(self, request, pk=None):
        try:
            order = self.get_object()
            
            if IsDeliveryCrew().has_permission(request, self):
                if order.status == 1:
                    return Response('Order has already been delivered. No data to show for u', 200)
            
            serializer = self.get_serializer(order)
            order_items = OrderItem.objects.filter(order=order)
            order_items_serializer = OrderItemSerializer(order_items, many=True)
            
            response_data = {
                'order': serializer.data,
                'order_items': order_items_serializer.data
            }
    
            return Response(response_data, 200)
        
        except Exception as e:
            return Response({'error':str(e)}, 404)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response('No cart items to create order with.', 400)
        
        total = 0
        
        for cart_item in cart_items:
            total += cart_item.price
            print(cart_item.price)
        
        order_data = {
            'user': user.id,
            'delivery_user_id': request.data.get('delivery_user_id'),
            'status': 0,
            'total': total,
            'date': timezone.now().date(),
        }
        
        order_serializer = self.get_serializer(data=order_data)
        order_serializer.is_valid(raise_exception=True)
        order_instance = order_serializer.save()
        
        if not order_instance.id:
            return Response({'error': 'Failed to create Order instance.'}, status=500)
        
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                order = order_instance,
                menuitem = cart_item.menuitem,
                quantity = cart_item.quantity,
                unit_price = cart_item.unit_price,
                price = cart_item.price
            )
            order_items.append(order_item)
        
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        
        return Response('Order created with all item from cart and cart items deleted successfully.', 200)
    
    @action(detail=True, methods=['put', 'patch'])
    def update_order_item(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            order = Order.objects.get(pk=pk)
            
            if request.user == order.user:
                return Response(f'No permission to update order #{pk}', 403)
            
            if IsManager().has_permission(request, self):
                if 'delivery_user_id' in request.data:
                    order.delivery_user_id = request.data['delivery_user_id']

                if 'status' in request.data:
                    order.status = request.data['status'].lower() == 'true'

            elif IsDeliveryCrew().has_permission(request, self):
                if 'status' in request.data:
                    order.status = request.data['status'].lower() == 'true'
                else:
                    return Response(f'No permission to update order #{pk} other than status', 403)

            order_serializer = OrderSerializer(order, data=request.data, partial=True)
            order_serializer.is_valid()
            order.save()

            response_data = {
                'order': order_serializer.data,
            }
            
            return Response(response_data, 200)
        
        except Exception as e:
            print(e)
            return Response(f'Order #{pk} not found', 404)
    
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            order = Order.objects.get(pk=pk)
            
            if request.user == order.user or IsManager().has_permission(request, self):
                order_items = OrderItem.objects.filter(order=order)
                order_items.delete()
                order.delete()
                return Response(f'Order #{pk} with order items deleted successfully.', 200)
            else:
                return Response(f'No permission to delete order #{pk}', 403)

        except Exception as e:
            print(e)
            return Response(f'Order #{pk} not found', 404)
from django.urls import path
from . import views

"""
#A viewset that provides default `create()`, `retrieve()`, `update()`,
#`partial_update()`, `destroy()` and `list()` actions.
"""

urlpatterns = [
    #path('categories', views.CategoryViewSet.as_view({'get':'list', 'post':'create', 'update':'update'})),
    # THAT'S THE IDEA ^^^
    # {'get':'list', 'post':'create', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}
        
    path('menu-items', views.MenuItemView.as_view({'get':'list', 'post':'create'})),
    path('menu-items/<int:pk>', views.MenuItemView.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),

    path('groups/manager/users', views.ManagerGroupView.as_view({'get':'list', 'post':'assign_to_manager_group'})),
    path('groups/manager/users/<int:pk>', views.ManagerGroupView.as_view({'get':'retrieve', 'delete':'remove_manager_role'})),

    path('groups/delivery-crew/users', views.DeliveryCrewGroupView.as_view({'get':'list', 'post':'assign_to_deliver_crew_group'})),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewGroupView.as_view({'get':'retrieve', 'delete':'remove_delivery_crew_role'})),

    path('cart/menu-items', views.CartView.as_view({'get':'list', 'post':'create', 'delete':'destroy'})),
    
    path('orders', views.OrderView.as_view({'get':'list', 'post':'create'})),
    path('orders/<int:pk>', views.OrderView.as_view({'get':'list_order_with_items', 'put':'update_order_item', 'patch':'update_order_item'})),
]
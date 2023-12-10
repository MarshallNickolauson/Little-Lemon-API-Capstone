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
        
    path('menu-items', views.MenuItemView.as_view({'get':'list', 'post':'create', 'update':'update', 'patch':'partial_update', 'delete':'destroy'})),
    path('menu-items/<int:pk>', views.MenuItemView.as_view({'get':'list', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),
]
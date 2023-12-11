from django.contrib import admin
from .models import *

class CategoryAdmin(admin.ModelAdmin):
    # Exclude the 'slug' field from the admin form
    exclude = ('slug',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem)

class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('unit_price', 'price')

admin.site.register(Cart, CartAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
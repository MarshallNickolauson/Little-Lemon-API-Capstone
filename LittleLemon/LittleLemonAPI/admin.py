from django.contrib import admin
from .models import *

class CategoryAdmin(admin.ModelAdmin):
    # Exclude the 'slug' field from the admin form
    exclude = ('slug',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
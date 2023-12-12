from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)
    
    def __str__(self):
        return self.title

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        featured_str = f" | Featured" if self.featured else ""
        return f"{self.title} | {self.category.title} | {self.price}{featured_str}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} {self.menuitem.title} in cart of User '{self.user.username}' | subtotal = {self.price}"

    def save(self, *args, **kwargs):
        self.unit_price = self.menuitem.price
        self.price = self.menuitem.price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('menuitem', 'user')

from django.utils import timezone

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)
    
    def save(self, *args, **kwargs):
        self.date = timezone.now().date()
        super().save(*args, **kwargs)
    
    # TODO total should be all cart items added and then saved here
    # TODO date should be current date of save execution
    
    def __str__(self):
        return "Order for " + self.user.username

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # TODO Saving to this model is just a copy of the Cart model. Transfer all fields to here

    def __str__(self):
        return "Order item for " + self.order.user.username 
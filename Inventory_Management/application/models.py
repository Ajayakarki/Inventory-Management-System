from ast import arg
from email.policy import default
from operator import mod
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

CATEGORY = (
    ('Electronic', 'Electronic'),
    ('Sport', 'Sport'),
    ('Stationary', 'Stationary'),
    ('Food', 'Food'),

)

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY)
    quantity = models.PositiveIntegerField(null=True)
    per_quantity = models.PositiveIntegerField(null=True)
    reorder_level = models.PositiveIntegerField(default=0, null=True, blank=True)
    product_in = models.PositiveIntegerField(default=0, null=True, blank=True)
    product_out = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_sales = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Product'

    def total_price(self):
        return self.quantity * self.per_quantity

    def item_sales(self):
        return self.product_out * self.per_quantity

    def save(self, *args, **kwargs):
        self.total_sales = self.product_out * self.per_quantity
        super(Product, self).save(*args, **kwargs)

        
    def __str__(self):
        return f'{self.name}-{self.quantity}'


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Order'

    def order_price(self):
        return self.order_quantity * self.product.per_quantity

    
    # def stockOut(self):
    #     return self.product.quantity - self.order_quantity
    
    

    def __str__(self):
        return f'{self.product} order by {self.customer.username}'



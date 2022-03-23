from django.contrib import admin
from .models import Product, Order

admin.site.site_header = 'My Inventory'

class AdminProduct(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', )
    list_filter = ['category']

# Register your models here.

admin.site.register(Product, AdminProduct)
admin.site.register(Order)

from django import forms
from .models import Product, Order



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'per_quantity', 'reorder_level']


    def clean_name(self):
        name = self.cleaned_data.get('name')

        for instance in Product.objects.all():
            if instance.name == name:
                raise forms.ValidationError(name + ' already exist')
        return name

class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'per_quantity', 'reorder_level']

class ProductQuantityUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_in']

class StaffOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'order_quantity']
    
    def clean(self):
        product_quantity = self.cleaned_data['product']
        order_quantity = self.cleaned_data['order_quantity']
        if(product_quantity.quantity < order_quantity):
            raise forms.ValidationError("Sorry that much stock is not available at the moment")


class ProductSearchForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name']


class CsvForm(forms.Form):
    csv = forms.BooleanField(required=False)
   



    
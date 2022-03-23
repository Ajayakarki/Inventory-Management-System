from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueTogetherValidator



from .models import Product, Order

from accounts.models import Profile



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'quantity', 'per_quantity', 'reorder_level']
        validators = [
            UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields = ['name']

            )
        ]
    
class ProductRetriveUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'quantity', 'per_quantity', 'reorder_level']


class ProductInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_in']


##### For Total Sales by staff in the inventory ################
class GetProudctSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name','category','per_quantity']

class GetCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    product = GetProudctSerializer()
    customer = GetCustomerSerializer()
    order_price = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['product', 'customer', 'order_quantity', 'date', 'order_price']
        #depth = 1

    def get_order_price(self, instance):
        return instance.order_price()

##### Order of a individual Staff #########
class StaffSalesSerializer(serializers.ModelSerializer):
    product = GetProudctSerializer()
    customer = GetCustomerSerializer()
    order_price = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['product', 'customer', 'order_quantity', 'date', 'order_price']
    
    def get_order_price(self, instance):
        return instance.order_price()


##### For creating the stafforder/sales

class StaffOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order 
        fields = ("order_quantity", "product")

   

###### Profile ########
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'image']


### For Regestration new User in the System
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'profile']
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "password didn't match"})
        return attrs


    ### For hasing the password
    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'],email=validated_data['email'])

        user.set_password(validated_data['password'])
        user.save()
        return user
    

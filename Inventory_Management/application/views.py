from itertools import product
from urllib import request
from django.http import JsonResponse
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Order
from .forms import ProductForm, StaffOrderForm, CsvForm, ProductUpdateForm, ProductSearchForm, ProductQuantityUpdateForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.db.models import Sum
import csv

from django.contrib.auth.decorators import permission_required


#################### DRF ####################

from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from .serializers import ProductSerializer, ProductRetriveUpdateDeleteSerializer, ProductInSerializer, UserSerializer, OrderSerializer, StaffSalesSerializer, StaffOrderCreateSerializer, ProfileSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from rest_framework.parsers import JSONParser, MultiPartParser

# Create your views here.

@login_required(login_url='login')
def index(request):

    orders = Order.objects.all()
    products = Product.objects.all()
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total = Product.objects.all().aggregate(thedata=Sum('total_sales'))


    workers_count = User.objects.all().count()
    products_count = products.count()
    orders_count = orders.count()
    product_sales_count = Product.objects.count()

    if request.method == 'POST':
        staff_order = StaffOrderForm(request.POST)
        #quan = products.product_in        
        if staff_order.is_valid():

            instance = staff_order.save(commit=False)
            instance.customer = request.user
            instance.product.quantity -= instance.order_quantity
            instance.product.product_out += instance.order_quantity
            instance.product.save()
            instance.save()
            return redirect('index')

    else:
        staff_order = StaffOrderForm()
    context = {
        'orders': orders,
        'products': products,

        'staff_order': staff_order,
        'page_obj': page_obj,

        'workers_count': workers_count,
        'products_count': products_count,
        'orders_count': orders_count,
        'product_sales_count': product_sales_count,

        'total': total,
    }
    return render(request, 'application/index.html', context)


def search(request):

    # orders = Order.objects.all()
    products = Product.objects.all()
    
    # For Searching
    search_post = request.GET.get('search')
    if search_post:
        search = Product.objects.filter(Q(name__icontains=search_post) | Q(category__icontains=search_post ))
        print(search)

    context = {
        'search': search,
        'products': products,
        
    }
    return render(request, 'application/search.html', context)






### For Displaying all the staff in the Inventory
@login_required(login_url='login')
@permission_required("application", login_url='login')

def staff(request):
    workers = User.objects.all()

    ##For counting the number in front
    workers_count = workers.count()
    products_count = Product.objects.all().count()
    orders_count = Order.objects.all().count()
    product_sales_count = Product.objects.count()
    

    context = {
        'workers': workers,

        'workers_count': workers_count,
        'products_count': products_count,
        'orders_count': orders_count,
        'product_sales_count': product_sales_count,
    }
    return render(request, 'application/staff.html', context)

### For viewing particular staff in the inventory
@login_required(login_url='login')
def staffDetail(request, pk):
    worker = User.objects.get(id=pk)
    context = {
        'worker': worker,
    }

    return render(request, 'application/staff_detail.html', context)

### Adding Products
def products(request):
    product = Product.objects.all().order_by('-product_out')

    products_count = product.count()
    workers_count = User.objects.all().count()
    orders_count = Order.objects.all().count()
    product_sales_count = Product.objects.count()

    paginator = Paginator(product, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    ## When Post request is called
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            print("Successfully created product ", name)
            messages.success(request, f"Successfully added product {name}")
            return redirect('products')
            
    else:
        form = ProductForm()
    
    context = {
        'product': product,
        'form': form,
        'page_obj': page_obj,

        'products_count': products_count,
        'workers_count': workers_count,
        'orders_count': orders_count,
        'product_sales_count': product_sales_count,

    }
    return render(request, 'application/products.html', context)

### Products deails with stock in and out
def productsInOut(request):
    product = Product.objects.all().order_by('-product_out')

    products_count = product.count()
    workers_count = User.objects.all().count()
    orders_count = Order.objects.all().count()
    product_sales_count = Product.objects.count()

    context = {
        'product': product,

        'products_count': products_count,
        'workers_count': workers_count,
        'orders_count': orders_count,
        'product_sales_count': product_sales_count,

    }
    return render(request, 'application/products_in_out.html', context)


def productStaff(request):
    product = Product.objects.all().order_by('-product_out')

    if 'term' in request.GET:
        result = Product.objects.filter(name__istartswith=request.GET.get('term'))
        titles = []
        for product in result:
            titles.append(product.name)
        return JsonResponse(titles, safe=False)

    context = {
        'product': product,
    }
    return render(request, 'application/products_staff.html', context)


### Searching Particular Products
def productsList(request):
    product = Product.objects.all()

    products_count = product.count()
    workers_count = User.objects.all().count()
    orders_count = Order.objects.all().count()
    product_sales_count = Product.objects.count()

    if request.method == 'POST':
        search_form = ProductSearchForm(request.POST)
        product = Product.objects.filter(category__icontains=search_form['category'].value(),
                                         name__icontains=search_form['name'].value(),
                                         )
    else:
        search_form = ProductSearchForm()

    context = {
        'product': product,
        'search_form': search_form,

        'products_count': products_count,
        'workers_count': workers_count,
        'orders_count': orders_count,
        'product_sales_count': product_sales_count,
    }

    return render(request, 'application/products_list.html', context)




## Details Update
def updateProduct(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductUpdateForm(instance=product)

    context = {
        'form': form,
    }

    return render(request, 'application/product_update.html', context)

## Product Quantity Updated
def updateQuantityProduct(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ProductQuantityUpdateForm(request.POST, instance=product)
        quan = product.product_in

        if form.is_valid():
            instance = form.save(commit=False)
            instance.quantity += instance.product_in
            instance.product_in = instance.product_in + quan

            #instance.product.save()
            instance.save()
            return redirect('products')

    else:
        form = ProductQuantityUpdateForm(instance=product)

    context = {
        'form': form,
    }

    return render(request, 'application/product_quantity_update.html', context)


def deleteProduct(request, pk):
    product = Product.objects.get(id = pk)
    if request.method == 'POST':
        product.delete()
        return redirect('products')
    return render(request, 'application/product_delete.html')


### Listing the Order request made by the Staffs
@permission_required("application", login_url='login')
def orders(request):
    ## For getting the particular sales list between date
    if request.method == 'POST':
        form = CsvForm(request.POST)

        fromdate = request.POST['fromdate']
        todate = request.POST['todate']

        finall = Order.objects.filter(date__gte=fromdate,date__lte=todate)
        print(finall)

        if form['csv'].value() == True:

            response = HttpResponse(content_type = 'text/csv')
            response['Content-Disposition'] = 'attachment; filename="Sales Details.csv"'
            writer = csv.writer(response)
            writer.writerow(['Product', 'Categoty', 'Quantity', 'Per_Unit', 'Total', 'Sales By', 'Date'])
            instance = finall
            for stock in instance:
                writer.writerow([
                    stock.product.name, stock.product.category, stock.order_quantity,
                    stock.product.per_quantity, stock.order_price(),
                    stock.customer.username, stock.date])
            return response

      

        ## COunting in frontend
        orders_count = Order.objects.all().count()
        workers_count = User.objects.all().count()
        products_count = Product.objects.all().count()
        product_sales_count = Product.objects.count()
        context = {
            'orders': finall,

            'form': form,
            'workers_count': workers_count,
            'products_count': products_count,
            'product_sales_count': product_sales_count,
            'orders_count': orders_count,
        }
    
        return render(request, 'application/orders.html', context)
    else:
        orders = Order.objects.all()
        form = CsvForm()
        ### For counting the number in frontend
        orders_count = orders.count()
        workers_count = User.objects.all().count()
        products_count = Product.objects.all().count()
        product_sales_count = Product.objects.count()

        context = {
            'orders': orders,

            'form': form,
            'orders_count': orders_count,
            'workers_count': workers_count,
            'products_count': products_count,
            'product_sales_count': product_sales_count,
        }
        return render(request, 'application/orders.html', context)


def csvDetails(request):
        order = Order.objects.all()
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename="Sales Details.csv"'
        writer = csv.writer(response)
        writer.writerow(['Product', 'Categoty', 'Quantity', 'Per_Unit', 'Total', 'Sales By', 'Date'])
        instance = order
        for stock in instance:
            writer.writerow([
                stock.product.name, stock.product.category, stock.order_quantity,
                stock.product.per_quantity, stock.order_price(),
                stock.customer.username, stock.date])
        return response

@permission_required("application", login_url='login')
def sales(request):
    product_sales = Product.objects.all()

    ### For counting the number in frontend
    product_sales_count = product_sales.count()
    orders_count = Order.objects.all().count()
    workers_count = User.objects.all().count()
    products_count = Product.objects.all().count()

    ## For calculating the total number of sales of all product
    total = Product.objects.all().aggregate(thedata=Sum('total_sales'))

    if request.method == 'POST':
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename="Sales of Inventory.csv"'
        writer = csv.writer(response)
        writer.writerow(['Product', 'Categoty', 'Quantity', 'Per_Unit', 'Sales'])
        instance = product_sales
        for stock in instance:
            writer.writerow([stock.name, stock.category, stock.quantity, stock.per_quantity, stock.total_sales])
        return response
    context = {

        'product_sales': product_sales,
        'total': total,

        'product_sales_count': product_sales_count,
        'orders_count': orders_count,
        'workers_count': workers_count,
        'products_count': products_count,

    }
    return render(request, 'application/sales.html', context)


#################### DRF #######################

class RegisterUserView(APIView):
    
    parser_classes = (JSONParser, MultiPartParser)


    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'status': 403, 'errors': serializer.errors, 'message': 'Something is wrong'})

        serializer.save()

        user = User.objects.get(username=serializer.data['username'])
        user = User.objects.get(email=serializer.data['email'])

        token_obj, _ = Token.objects.get_or_create(user=user)

        return Response({'status': 200, 'payload': serializer.data, 'errors': serializer.errors, 'token': str(token_obj), 'message': 'Successfully regestered'})

    def get(self, request, pk=None, format=None):
        id = pk
        if id is not None:
            user_obj = User.objects.get(id=id)
            serializer = UserSerializer(user_obj)   ## data = request.data
            return Response({'status':200, 'payload': serializer.data})
        user_obj = User.objects.all()
        serializer = UserSerializer(user_obj, many=True) 
        return Response({'status': 200, 'payload': serializer.data})

    
    def put(self, request, pk=None):
        user = User.objects.get(pk=pk)
        profile = user.profile
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

    

### For displaying all the products
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAdminUser]


### For adding new products
class ProductCreateView(CreateAPIView):
    #queryset = Product.objects.all()
    serializer_class = ProductSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

class ProductUpdateDeleteViewRetriveView(UpdateAPIView,DestroyAPIView,RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductRetriveUpdateDeleteSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'


#### For Order ####

### For displaying all the products
class OrderListView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

#### For Displaying individul staff
class StaffOrderListView(ListAPIView):
    serializer_class = StaffSalesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        #user = self.request.user
        return Order.objects.filter(customer_id=self.kwargs['customer_id'])


class StaffOrderCreateCreateView(CreateAPIView):
    serializer_class = StaffOrderCreateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StaffOrderCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'status': 403, 'errors': serializer.errors, 'message': 'Something went wrong'})

        product = Product.objects.get(id=request.data['product'])
        order_quantity=request.data['order_quantity']
        

        if order_quantity > product.quantity:
            return Response({'status': 403, 'message': 'Maximum Order Quantity'})

        
        serializer.save(customer=self.request.user)

        product.product_out += order_quantity
        
        product.quantity -= order_quantity

        

        product.save()
        #serializer.save(customer=self.request.user)

        return Response({'status': 200, 'payload': serializer.data, 'message': 'Successfully regestered'})


class ProductInCreateView(CreateAPIView):
    serializer_class = ProductInSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


    def put(self, request): 
        serializer = ProductInSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'status':400, 'errors': serializer.errors, 'message': 'Something is wrong'})


        product = Product.objects.get(id=request.data['id'])
        product_in_instance = request.data['product_in']

        product.product_in = product.product_in + product_in_instance
        product.quantity += product_in_instance

        

        product.save()
        #serializer.save()


        return Response({'status': 200, 'payload': serializer.data, 'message': 'Quantity added'})



        

    

    
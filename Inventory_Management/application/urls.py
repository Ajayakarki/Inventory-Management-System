from django.urls import path ,include
from .import views

###### DRF ###########
from rest_framework.authtoken import views as rest_views


urlpatterns = [
    path('dashboard/', views.index, name='index'),
    path('staff/', views.staff, name='staff'),
    path('staff/detail/<int:pk>', views.staffDetail, name='staff_detail'),
    path('products/', views.products, name='products'),
    path('products_in_out/', views.productsInOut, name='products-in-out'),
    path('products/list', views.productsList, name='products-list'),
    path('products/staff', views.productStaff, name='products-staff'),
    path('products/update/<int:pk>/', views.updateProduct, name='product_update'),
    path('products_quantity/update/<int:pk>/', views.updateQuantityProduct, name='product_quantity_update'),
    path('products/delete/<int:pk>/', views.deleteProduct, name='product_delete'),
    path('search/', views.search, name='search'),
    path('details/', views.orders, name='orders'),

    path('detailscsv/', views.csvDetails, name='detail_csv'),



    path('sales/', views.sales, name='sales'),

    #################### DRF ###########################
    path('api/', views.ProductListView.as_view(), name='api_product_list'),
    path('api/create/', views.ProductCreateView.as_view(), name='api_product_create'),
    path('api/action/<int:pk>/', views.ProductUpdateDeleteViewRetriveView.as_view(), name='api_action'),

    path('api/productin/', views.ProductInCreateView.as_view(), name='product_inn'),

    
    path('api/orders/', views.OrderListView.as_view(), name='api_order_list'),
    path('api/stafforders/<int:customer_id>/', views.StaffOrderListView.as_view(), name='api_stafforder_list'),

    path('api/stafforders/create/', views.StaffOrderCreateCreateView.as_view(), name='api_stafforder_create'),



    # ### Session Authentication buildin Login and Logout of DRF
    # path('auth/', include('rest_framework.urls')),


    path('api-token-auth/', rest_views.obtain_auth_token),
    path('api/register/', views.RegisterUserView.as_view()),
    path('api/register/<int:pk>/', views.RegisterUserView.as_view()),
    path('api/register/<int:pk>/profile/', views.RegisterUserView.as_view()), 








]
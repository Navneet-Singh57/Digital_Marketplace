from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.index,name="index"),
    path('home/',views.home,name="home"),
    path('product/<int:pk>',views.detail,name="detail"),
    path('success/',views.payment_success_view,name="success"),
    path('failed/',views.payment_failed_view,name="failed"),
    path('api/checkout-session/<int:id>',views.create_checkout_session,name="api_checkout_session"),
    path('create_product/',views.create_product,name="create_product"),
    path('edit_product/<int:id>/',views.edit_product,name="edit_product"),
    path('delete/<int:id>',views.delete_product,name="delete"),
    path('dashboard/',views.dashboad,name="dashboard"),
    path('register/',views.register,name="register"),
    path('login/',auth_views.LoginView.as_view(template_name="myapp/login.html"),name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('invalid/',views.invalid,name="invalid"),
    path('purchases/',views.mypurchases,name="purchases"),
    path('sales/',views.sales,name="sales"),
]
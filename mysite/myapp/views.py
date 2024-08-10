from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse,HttpResponseNotFound
from .models import Product,OrderDetail
from django.conf import settings
import stripe,json
from django.views.decorators.csrf import csrf_exempt
from .forms import ProductForm, UserRegistrationForm
from django.contrib.auth import logout
from django.db.models import Sum

# Create your views here.

def home(request):
    products = Product.objects.all()
    context = {
        'products' : products
    }
    return render(request,'myapp/index.html',context)

def index(request):
    products = Product.objects.all()
    context = {
        'products' : products
    }
    return render(request,'myapp/index.html',context)

def detail(request,pk):
    product = Product.objects.get(id=pk)
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    context = {
        'product' : product,
        'stripe_publishable_key' : stripe_publishable_key,
    }
    return render(request,'myapp/detail.html',context)

@csrf_exempt
def create_checkout_session(request,id):
    request_data = json.loads(request.body)
    product = Product.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = request_data['email'],
        payment_method_types = ['card'],
        line_items = [
            {
                'price_data':{
                    'currency':'usd',
                    'product_data':{
                        'name':product.name,
                        
                    },
                    'unit_amount' : int(product.price * 100)
                },
                'quantity':1,
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse('success')) +
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse('failed')),
    )
    
    order = OrderDetail()
    order.customer_email = request_data['email']
    order.product = product
    order.stripe_payment_intent = checkout_session['payment_intent']
    order.amount = int(product.price)
    order.save()
    
    return JsonResponse({'sessionID':checkout_session.id})

def payment_success_view(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    order = get_object_or_404(OrderDetail,stripe_payment_intent=session.payment_intent)
    order.has_paid=True
    product = Product.objects.get(id=order.product.id)
    product.total_sales_amount += int(product.price)
    product.total_sales += 1
    product.save()
    order.save()
    
    return render(request,'myapp/payment_success.html',{'order':order})

def payment_failed_view(request):
    return render(request,'myapp/failed.html')


def create_product(request):
    form = ProductForm
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            newproduct = form.save(commit=False)
            newproduct.seller = request.user
            newproduct.save()
            return redirect('index')
    context={
        'form':form
    }
    return render(request,'myapp/create_product.html',context)

def edit_product(request,id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    form = ProductForm(request.POST or None,request.FILES or None,instance=product)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('index')
    context={
        'form':form,
        'product':product
    }
    return render(request,'myapp/product_edit.html',context)

def delete_product(request,id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    if request.method == "POST":
        product.delete()
        return redirect('index')
    return render(request,'myapp/delete.html',{'product':product})
    
def dashboad(request):
    products = Product.objects.filter(seller=request.user)
    return render(request,'myapp/dashboard.html',{'products':products})

def register(request):
    if request.method == "POST":
        userform = UserRegistrationForm(request.POST)
        newuser = userform.save(commit=False)
        newuser.set_password(userform.cleaned_data['password'])
        newuser.save()
        return redirect('index')
    userform = UserRegistrationForm()
    return render(request,'myapp/register.html',{'userform':userform})

def logout_view(request):
    logout(request)
    return render(request,'myapp/logout.html')


def invalid(request):
    return render(request,'myapp/invalid.html')

def mypurchases(request):
    orders = OrderDetail.objects.filter(customer_email=request.user.email)
    return render(request,'myapp/purchases.html',{'orders':orders})

def sales(request):
    orders = OrderDetail.objects.filter(product__seller=request.user)
    total_sales = orders.aggregate(Sum('amount'))
    return render(request,'myapp/sales.html',{'total_sale':total_sales})
    
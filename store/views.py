import django
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from store.models import Address, Cart, Category, Order, Product,Email,Contactus
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from .models import *
from django.contrib import messages
import ssl
from .models import OTP_Data
import random
import smtplib
from email.message import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from verify_email.email_handler import send_verification_email
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages #import messages
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponse
import datetime
import stripe


# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    if request.method=="POST":
        SUBSCRIBER=request.POST.get('email')
        data=Email(Email=SUBSCRIBER)
        data.save()
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)

@login_required
def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})

@login_required
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here
class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            inactive_user = send_verification_email(request, form)
            messages.success(request, "Congratulations! Registration Successful!")
        return render(request, 'account/register.html', {'form': form})
    
@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    messages.success(request, "Product Added Succesfully")
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def add_to_likeproduct(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_wishlist = Wishlist.objects.filter(product=product_id, user=user)
    if item_already_in_wishlist:
        cp = get_object_or_404(Wishlist, product=product_id, user=user)
        cp.save()
    else:
        Wishlist(user=user, product=product).save()
    messages.success(request, "Product Added Succesfully")
    return redirect('store:likeproduct')

@login_required
def likeproduct(request):
    user = request.user
    cart_products = Wishlist.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)

    context = {
        'cart_products': cart_products,
        'amount': amount,
    }
    return render(request, 'store/likeproduct.html', context)


@login_required
def remove_likeproduct(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Wishlist, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from likedproduct.")
    return redirect('store:likeproduct')


@login_required
def plus_likeproduct(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Wishlist, id=cart_id)
        cp.save()
    return redirect('store:likeproduct')


@login_required
def minus_likeproduct(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Wishlist, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:likeproduct')




@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





def testimonials(request):
    return render(request, 'store/testimonials.html')

def services(request):
    return render(request, 'store/services.html')

@login_required
def contact(request):
    if request.method=='POST':
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        phone=request.POST['phone']
        jwelery=request.POST['jwelery']
        design=request.FILES['design']
        subject=request.POST['subject']
        newcontact=Contactus.objects.create(firstname=firstname,lastname=lastname,phone=phone,jwelery=jwelery,design=design,subject=subject)  
        newcontact.save()
        messages.success(request, "Your Message send suucesfully!")
    return render(request, 'store/contact.html')

def forgot_otp(request):
    enable_otp = 0
    if request.method == "POST":
        email = request.POST.get("email_id")
        user = User.objects.filter(username = email)
        print(user)
        if user is not None:
            otp_generate = random.randrange(1000, 9999)
            # email_sender = 'manavmandli2990@gmail.com'
            # email_password = 'bgcegdcrigfwxuja'
            email_sender = 'goldwholesalingandretailing@gmail.com' 
            email_password = 'pgtxndovhrlztkly'
            email_receiver = email
            subject = "OTP"
            body = """
            Welcome to GWR 
            Your OTP is - {}""".format(otp_generate)
            em = EmailMessage()
            em['from'] = email_sender
            em['to'] = email_receiver
            em['subject'] = subject
            em.set_content(body)
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com',465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender,email_receiver,em.as_string())
            enable_otp = 1
            OTP_data = OTP_Data(email_id = email,otp = otp_generate)
            OTP_data.save()
            return render(request,'account/forgot.html',{"enable_otp":enable_otp})
        else:
            messages.warning(request,"Please Enter Valid username and Password")
    return render(request,'account/forgot.html')

def forgot_pass(request):
    if request.method == "POST":
        email = request.POST.get("mail_id")
        print(email)
        otp = request.POST.get("otp")
        mydata = OTP_Data.objects.filter(email_id=email).values()
        print(mydata)
        otp_field = str(mydata)[-7:-3]
        print(otp_field)
        if otp == otp_field:
            otp_data = OTP_Data.objects.filter(email_id = email)
            otp_data.delete()
            local_data = 1
            return render(request,"account/forgot_pass.html",{"local_data":local_data})
        else:
            enable_otp = 1
            messages.warning(request,"Please Enter Valid OTP")
            return render(request,"account/forgot.html",{"enable_otp":enable_otp})
    return render(request,'account/forgot.html')

def new_pass(request):
    if request.method == "POST":
        email = request.POST.get("mail_id")
        password = request.POST.get("pass")
        cpassword = request.POST.get("cpass")
        if password == cpassword:
            user = User.objects.get(email = email)
            user.set_password(password)
            user.save()
            messages.success(request,"Your password has been changed")
            return redirect("store:login")
        else:
            messages.warning(request,"Doesn't match password")
            return render(request,"account/forgot_pass.html")
    return redirect("account/login.html")


stripe.api_key = 'sk_test_51MedHmSHJDFuPL5cnRItHVU94xOAzKltL5vuoADjGI0wZfVNRtCwU3I3eKgvtQUF0z3w2yl5IuQ5rRZcOs9m2ytj00YSZRJhjw'
def checkout(request):
    user = request.user
    total_price = 0
    cart_data = Cart.objects.filter(user=user).all().values()
    line_items = []
    total_price = 0
    for i in range(0,len(cart_data)):
        product_id = cart_data[i]["product_id"]
        product_data = Product.objects.filter(id = product_id).all().values()[0]
        total_price = total_price + product_data["price"]
        line_items.append(
        {
            'price_data': {
                'currency': 'inr',
                'product_data': {
                'name': product_data["title"],
                },
                'unit_amount': int(product_data["price"] * 100),
            },
            'quantity': cart_data[i]["quantity"],
        })
    subject = 'Payment Received'
    main_str = ""
    for i in cart_data:
        product_id = i["product_id"]
        product_name = Product.objects.filter(id = product_id).values()[0]["title"]
        qty = i["quantity"]
        newstr = "Product Name -> {}   Qty -> {}\n".format(product_name,qty)
        main_str = main_str + newstr
    message = f'''Your payment has been Succesfully Received...\n
Cart Product:-\n
Order Items:-\n{main_str}
Total Price:- {total_price}\n
Thanks {user.email} Shopping From GWR'''
    from_email = 'goldwholesalingandretailing@gmail.com'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    session = stripe.checkout.Session.create(
    line_items= line_items,
    mode='payment',
    success_url='http://127.0.0.1:8000/success',   
    cancel_url='http://127.0.0.1:8000/cancle',
    )
    return redirect(session.url, code=303)



def success(request):
    user = request.user
    cart_item = Cart.objects.filter(user = user).all().values()
    for i in cart_item:
        print(i)
        order_item = Order()
        order_item.user = user
        # order_item.address=i["address"]
        order_item.address=Address.objects.get(id=15)
        order_item.product = Product.objects.get(id=i["product_id"])
        order_item.quantity = i["quantity"]
        today_date = datetime.date.today()
        order_item.ordered_date = today_date
        order_item.save()
    Cart.objects.filter(user = user).delete()
    return render(request,"store/success.html")

def cancle(request):
    return render(request,"store/cancle.html")

def cod(request):
    user = request.user
    address_id = request.GET.get('address')
    
    if address_id is None:
        return HttpResponse("Go back and select Your Address")
    else:
        address = get_object_or_404(Address, id=address_id)
        # Get all the products of User in Cart
        cart = Cart.objects.filter(user=user)
        for c in cart:
            # Saving all the products from Cart to Order
            Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
            # And Deleting from Cart
            c.delete()
        return redirect('store:orders')
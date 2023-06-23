from store.forms import LoginForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


app_name = 'store'


urlpatterns = [
    path('', views.home, name="home"),
    # URL for Cart and Checkout
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-cart/<int:cart_id>/', views.remove_cart, name="remove-cart"),
    path('plus-cart/<int:cart_id>/', views.plus_cart, name="plus-cart"),
    path('minus-cart/<int:cart_id>/', views.minus_cart, name="minus-cart"),
    path('cart/', views.cart, name="cart"),
    
    path('add-to-likeproduct/', views.add_to_likeproduct, name="add-to-likeproduct"),
    path('remove-likeproduct/<int:cart_id>/', views.remove_likeproduct, name="remove-likeproduct"),
    path('plus-likeproduct/<int:cart_id>/', views.plus_likeproduct, name="plus-likeproduct"),
    path('minus-likeproduct/<int:cart_id>/', views.minus_likeproduct, name="minus-likeproduct"),
    path('likeproduct/', views.likeproduct, name="likeproduct"),
    path('orders/', views.orders, name="orders"),

    #URL for Products
    path('product/<slug:slug>/', views.detail, name="product-detail"),
    path('categories/', views.all_categories, name="all-categories"),
    path('<slug:slug>/', views.category_products, name="category-products"),

    # URL for Authentication
    path('accounts/register/', views.RegistrationView.as_view(), name="register"),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='account/login.html', authentication_form=LoginForm), name="login"),
    path('accounts/profile/', views.profile, name="profile"),
    path('accounts/add-address/', views.AddressView.as_view(), name="add-address"),
    path('accounts/remove-address/<int:id>/', views.remove_address, name="remove-address"),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='store:login'), name="logout"),

    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='account/password_change.html', form_class=PasswordChangeForm, success_url='/accounts/password-change-done/'), name="password-change"),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name="password-change-done"),


    path('testimonials', views.testimonials, name="testimonials"),
    path('services', views.services, name="services"),
    path('contact',views.contact,name="contact"),
    
    path('forgot_otp',views.forgot_otp,name="forgot_otp"),
    path('forgot_password',views.forgot_pass,name="forgot_pass"),
    path('new_pass',views.new_pass,name="new_pass"),
    path("checkout",views.checkout,name="checkout"),
    path("cod",views.cod,name="cod"),
    path('success',views.success,name="success"),
    path('cancle',views.cancle,name="cancle"),
    
    # path('verification/', include('verify_email.urls')),	
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

from django.urls import path, re_path
from . import views
from .views import navitem_detail, car_details

urlpatterns = [
    # Public urls
    path('', views.index, name='index'),
    path('customer-register-community/', views.get_register_community, name='customer_register_community'),
    path('customer-register-page/', views.register_page, name='register_page'),
    path('customer-register/', views.get_register, name='customer_register'),
    path('customer-login/', views.custom_login, name='customer_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('about-us/', views.about, name='about'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('save-contact/', views.save_contact, name='save_contact'),

    path('create-account-before-checkout/', views.create_account_before_checkout, name='create_account_before_checkout'),
    # path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('my-vehicles/', views.my_vehicles, name='my_vehicles'),
    path('my-vehicle-details/', views.my_vehicle_details, name='my_vehicle_details'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('customer-message/', views.customer_message, name='customer_message'),
    
    path('genz-blog/', views.blog, name='blog'),
    path('genz-blog-details/', views.blog_details, name='blog_details'),
    # path('<slug:slug>/', navitem_detail, name='navitem_detail'),
    path('<slug:slug>/', car_details, name='car_details'),
    
]

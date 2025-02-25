from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public urls
    path('', views.index, name='index'),
    path('customer-register-community/', views.get_register_community, name='customer_register_community'),
    path('customer-onboarding/', views.register_page, name='register_page'),
    path('customer-register/', views.get_register, name='customer_register'),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path('customer-login/', views.custom_login, name='customer_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('about-us/', views.about, name='about'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('save-contact/', views.save_contact, name='save_contact'),

    path('lock-your-price-now/<slug:slug>/', views.lock_your_price_now, name='lock_your_price_now'),
    path('create-account-before-checkout/', views.create_account_before_checkout, name='create_account_before_checkout'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    
    path('payment-history/', views.payment_history, name='payment_history'),
    path('my-vehicles/', views.my_vehicles, name='my_vehicles'),
    path('email-verify-from-dashboard', views.email_verify_from_dashboard, name='email_verify_from_dashboard'),
    path('my-vehicle-details/<uuid:id>/', views.my_vehicle_details, name='my_vehicle_details'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('customer-message/', views.customer_message, name='customer_message'),
    path('genz-blog/', views.blog, name='blog'),
    path('genz-blog-details/', views.blog_details, name='blog_details'),
    # path('<slug:slug>/', navitem_detail, name='navitem_detail'),
    path("car-selector/", views.car_selector, name="car_selector"),  # Fixed URL
    path('<slug:slug>/', views.reserve_now, name='car_details'),  # Slug should be last
    
]+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public urls
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
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

    path('tech-specs/<slug:slug>/', views.tech_specs, name='tech_specs'),
    path('learn-more/<slug:slug>/', views.learn_more, name='learn_more'),
    path('lock-your-price-now/<slug:slug>/', views.lock_your_price_now, name='lock_your_price_now'),
    path('create-account-before-checkout/', views.create_account_before_checkout, name='create_account_before_checkout'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    
    path('payment-history/', views.payment_history, name='payment_history'),
    path('my-vehicles/', views.my_vehicles, name='my_vehicles'),
    path('my-configurations/', views.my_configurations, name='my_configurations'),
    path('my-package-bookings/', views.my_package_bookings, name='my_package_bookings'),
    path('email-verify-from-dashboard', views.email_verify_from_dashboard, name='email_verify_from_dashboard'),
    path("send-otp/", views.send_otp_view, name="send_otp"),
    path("otp-verification/", views.otp_verify_page, name="otp_verify_page"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path('my-vehicle-details/<uuid:id>/', views.my_vehicle_details, name='my_vehicle_details'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('customer-message/', views.customer_message, name='customer_message'),
    path('genz-blog/', views.blog, name='blog'),
    path('genz-blog-details/', views.blog_details, name='blog_details'),
    path('<slug:slug>/', views.navitem_detail, name='navitem_detail'),
    path("car-selector/", views.car_selector, name="car_selector"),  # Fixed URL
    path('discount/<slug:slug>/', views.reserve_now, name='car_details'),  # Slug should be last
    path('new/car/configurator/<slug:slug>/', views.new_car_configurator, name='car_configurator'),
    path('car/configurator/<slug:slug>/', views.car_configurator, name='car_configurator_slug'),

    path('configuration/<slug:config_id>/', views.view_configuration, name='car_configuration_detail'),
    path('car/checkout/', views.checkout, name='checkout'),
path('car/reservation-checkout/<str:id>/', views.reservation_checkout, name='reservation_checkout'),  
 path('car/process-reservation/', views.process_reservation_payment, name='process_reservation_payment'),
    path('car/create-package-checkout-session/', views.create_package_checkout_session, name='create_package_checkout_session'),
    path('car/reservation_success/<str:id>/', views.reservation_success, name='reservation_success'),

]+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

from django.urls import path, re_path
from . import views
from .views import navitem_detail

urlpatterns = [
    # Public urls
    path('', views.index, name='index'),
    path('customer-login/', views.custom_login, name='customer_login'),
    path('customer-register/', views.get_register, name='customer_register'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('about-us/', views.about, name='about'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('save-contact/', views.save_contact, name='save_contact'),
    
    path('genz-blog/', views.blog, name='blog'),
    
    path('<slug:slug>/', navitem_detail, name='navitem_detail'),
]

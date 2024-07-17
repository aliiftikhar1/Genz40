from django.urls import path, re_path
from . import views
from .views import navitem_detail

urlpatterns = [
    # Public urls
    path('', views.index, name='index'),

    path('about-us/', views.about, name='about'),
    path('genz-blog/', views.blog, name='blog'),
    path('<slug:slug>/', navitem_detail, name='navitem_detail'),
]

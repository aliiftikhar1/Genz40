from django.urls import path, re_path
from . import views
from .views import navitem_detail, about

urlpatterns = [
    # Public urls
    path('', views.index, name='index'),
    path('<slug:slug>/', navitem_detail, name='navitem_detail'),
    path('<slug:slug>/', about, name='about'),
    path('genz-blog/', views.blog, name='blog'),
]

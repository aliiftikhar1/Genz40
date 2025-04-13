from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from . import views
from .views import register, CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordChangeView, custom_logout, package_list, package_add, package_edit, package_activate, package_deactivate

from frontend.views import car_configurator
# app_name = 'auth'

urlpatterns = [
    # Admin urls
    path('register/', register, name='register'),
#     path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),
    path('password_reset_done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
#     path('dashboard/', views.dashboard, name='dashboard'),

    # Navigation
    path('nav-items', views.navitem_list, name='navitem_list'),
    path('add/', views.navitem_add, name='navitem_add'),
    path('edit/<uuid:id>/', views.navitem_edit, name='navitem_edit'),
    path('activate/<uuid:id>/', views.navitem_activate, name='navitem_activate'),
    path('deactivate/<uuid:id>/', views.navitem_deactivate, name='navitem_deactivate'),
    path('upload-images/', views.upload_images, name='create_parent_and_images'),

    path('customer-list', views.customer_list, name='customer_list'),
    path('community-member-list', views.community_member_list, name='community_member_list'),
    path('subscriber-list', views.subscriber_list, name='subscriber_list'),

    
    path('packages/', package_list, name='package_list'),
    path('packages/add/', package_add, name='package_add'),
    path('packages/edit/<uuid:pk>/', package_edit, name='package_edit'),
    path('packages/activate/<uuid:pk>/', package_activate, name='package_activate'),
    path('packages/deactivate/<uuid:pk>/', package_deactivate, name='package_deactivate'),

    path('post-package-detail/add/', views.create_or_edit_post_package_detail, name='add_post_package_detail'),
    path('post-package-detail/edit/<int:pk>/', views.create_or_edit_post_package_detail, name='edit_post_package_detail'),
    path('post-package-detail/toggle/<int:pk>/', views.toggle_post_package_detail, name='toggle_post_package_detail'),

    path('post-package-feature/add/', views.create_or_edit_post_package_feature, name='add_post_package_feature'),
    path('post-package-feature/edit/<int:pk>/', views.create_or_edit_post_package_feature, name='edit_post_package_feature'),
    path('post-package-feature/toggle/<int:pk>/', views.toggle_post_package_feature, name='toggle_post_package_feature'),

    path('post-part/add/', views.create_or_edit_post_part, name='add_post_part'),
    path('post-part/edit/<int:pk>/', views.create_or_edit_post_part, name='edit_post_part'),
    path('post-part/toggle/<int:pk>/', views.toggle_post_part, name='toggle_post_part'),

    path('post-charging/add/', views.create_or_edit_post_charging, name='add_post_charging'),
    path('post-charging/edit/<int:pk>/', views.create_or_edit_post_charging, name='edit_post_charging'),
    path('post-charging/toggle/<int:pk>/', views.toggle_post_charging, name='toggle_post_charging'),

    path('post-paint/add/', views.create_or_edit_post_paint, name='add_post_paint'),
    path('post-paint/edit/<int:pk>/', views.create_or_edit_post_paint, name='edit_post_paint'),
    path('post-paint/toggle/<int:pk>/', views.toggle_post_paint, name='toggle_post_paint'),

    path('package-details/<uuid:pk>/', views.all_package_details, name='package_details'),

    path('reserved-cars/', views.reserved_car_list, name='reserved_car_list'),


    # path('car/configurator/<slug:slug>/', car_configurator, name="backend_car_configurator"),

    # URL to handle saving the car configuration
    path('save-car-configuration/', views.save_car_configuration, name='save_car_configuration'),
    
    # URL to list all available car models
    path('car-models/', views.car_models, name='car_models'),
    
    # URL to view saved configurations
    path('saved-configurations/', views.saved_configurations, name='saved_configurations'),
    
    # URL to view a specific saved configuration
    # path('configuration/<int:config_id>/', views.view_configuration, name='view_configuration'),
    

path('resrvations/', views.booked_package_list, name='booked_package_list'),

# new configurations system
 path('booked-packages/', views.get_all_booked_packages, name='get-all-booked-packages'),
    path('booked-packages/<uuid:pk>/', views.get_booked_package_by_id, name='get-booked-package-by-id'),
    path('booked-packages/user/<uuid:user_id>/', views.get_booked_packages_by_user_id, name='get-booked-packages-by-user-id'),
    path('booked-packages/create/', views.save_booked_package, name='save-booked-package'),
    path('booked-packages/update/<uuid:pk>/', views.update_booked_package, name='update-booked-package'),
    path('booked-packages/delete/<uuid:pk>/', views.delete_booked_package, name='delete-booked-package'),

]
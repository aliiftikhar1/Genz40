from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, PostCommunity, PostCommunityJoiners, PostPackageDetail, PostPackageFeature, PostPart, PostCharging, PostPaint, PostPayment, PostSubscribers
from .forms import CustomPasswordResetForm, CustomPasswordResetConfirmForm, PostPackageDetailForm, PostPackageFeatureForm, PostPartForm, PostChargingForm, PostPaintForm, \
    ImageModelForm
from .forms import RegisterForm, PostPackageForm, PostNavItemForm
from .models import PostPackage, PostNavItem,CarConfiguration
import string
import random
from common.utils import get_client_ip, send_custom_email
import requests
from decimal import Decimal
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import BookedPackage
from .serializers import BookedPackageSerializer


def clean_price_value(value):
    if value is None or value == '':
        return None
    try:
        # Ensure we're working with a string without any currency symbols or commas
        clean_value = str(value).replace('$', '').replace(',', '')
        return Decimal(clean_value)
    except:
        raise ValueError(f"'{value}' is not a valid decimal number")

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class CustomSortableUpdateView(View):
    def post(self, request, *args, **kwargs):
        # Handle sorting update logic here
        # This is just an example, you'll need to implement the actual sorting logic
        return JsonResponse({'status': 'ok'})

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def get_country_info(request):
    ip = get_client_ip(request)
    return ip

def register(request):
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    form = RegisterForm()
    random_password = generate_random_password()
    context = {
            'country_code': country_code,
            'country_flag_url': country_flag_url,
            'random_password': random_password,
            'form': form
        }

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(random_password)
            user = form.save()
             # Create a new UserProfile record
            # PostCommunity.objects.create(user=user, name='GENZ40', description='community_description')  # Modify or add fields as necessary
            # login(request, user)

            # template_name = "email/welcome_email.html"
            # subject = request.POST.get('subject', 'Default Subject')
            # message = request.POST.get('message', 'No message provided.')
            # recipient_email = request.POST.get('email', 'arvind.blues@gmail.com')
            # context = {
            #     'user': user,
            #     'password': random_password
            # }
            # send_custom_email(
            #     template_name,
            #     subject=subject,
            #     message=context,
            #     recipient_list=[recipient_email],
            # )


            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RegisterForm()
        # # ip = get_country_info(request)
        # response = requests.get(f'https://ipinfo.io/{ip}/json')
        # data = response.json()
        # country_code = data.get('country')
        # # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
        # country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    return render(request, 'registration/register.html', context)


# def custom_login(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             print('--------user details', user)
#             return redirect('dashboard')
#         else:
#             messages.error(request, 'Invalid username or password')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    form_class = CustomPasswordResetForm
    success_message = "An email with instructions to reset your password has been sent to %(email)s."
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = CustomPasswordResetConfirmForm
    success_message = "Your password has been reset successfully. You can now log in with the new password."
    success_url = reverse_lazy('customer_login')


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_message = "Your password has been changed successfully."
    success_url = reverse_lazy('password_change_done')


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')


# @login_required
# def dashboard(request):
#     header = 'Dashboard'
#     if request.user.role == 'admin':
#         return render(request, "admin/dashboard.html", {'header': header })
#     else:
#         return render(request, "customer/dashboard.html", {'header': header })


@login_required
def navitem_list(request):
    nav_items = PostNavItem.objects.all().order_by('position')
    return render(request, 'admin/navbar/list.html', {'nav_items': nav_items})


@login_required
def navitem_add(request):
    if request.method == 'POST':
        form = PostNavItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Added successfully')
            return redirect('navitem_list')
    else:
        form = PostNavItemForm()
    return render(request, 'admin/navbar/form.html', {'form': form})


@login_required
def navitem_edit(request, id):
    nav_item = get_object_or_404(PostNavItem, id=id)
    if request.method == 'POST':
        form = PostNavItemForm(request.POST, instance=nav_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Updated successfully')
            return redirect('navitem_list')
    else:
        form = PostNavItemForm(instance=nav_item)
    return render(request, 'admin/navbar/form.html', {'form': form, 'content': nav_item.content})


@login_required
def navitem_activate(request, id):
    nav_item = get_object_or_404(PostNavItem, id=id)
    nav_item.is_active = True
    nav_item.save()
    messages.success(request, 'Activated successfully')
    return redirect('navitem_list')


@login_required
def navitem_deactivate(request, id):
    nav_item = get_object_or_404(PostNavItem, id=id)
    nav_item.is_active = False
    nav_item.save()
    messages.success(request, 'Deactivated successfully')
    return redirect('navitem_list')


@login_required
def upload_images(request):
    if request.method == 'POST':
        form = ImageModelForm(request.POST, request.FILES)
        # nav_id = form.data['nav_item']
        if form.is_valid():
            form.save()
            # nav_id = form.cleaned_data['nav_item']
            # for img in request.FILES.getlist('image'):
            # PostImage.objects.create(nav_item=nav_id , image=img)
            messages.success(request, 'Image uploaded successfully')
            return redirect('create_parent_and_images')
    else:
        form = ImageModelForm()
    return render(request, 'admin/navbar/add_images.html', {'form': form})

@login_required
def customer_list(request):
    header = 'Customers'
    cutomers = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'admin/customer/list.html', {'cutomers': cutomers,'header':header})


@login_required
def package_list(request):
    all_package_list = PostPackage.objects.all()
    return render(request, 'admin/package/list.html', {'packages': all_package_list})

@login_required
def booked_package_list(request):
    all_booked_package_list = BookedPackage.objects.all()
    return render(request, 'admin/booked_package/list.html', {'booked_packages': all_booked_package_list})


@login_required
def package_add(request):
    if request.method == 'POST':
        form = PostPackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package added successfully')
            return redirect('package_list')
    else:
        form = PostPackageForm()
    return render(request, 'admin/package/form.html', {'form': form})


@login_required
def package_edit(request, pk):
    package = get_object_or_404(PostPackage, pk=pk)
    if request.method == 'POST':
        form = PostPackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package updated successfully')
            return redirect('package_list')
    else:
        form = PostPackageForm(instance=package)
    return render(request, 'admin/package/form.html', {'form': form, 'description': package.description})


@login_required
def package_activate(request, pk):
    package = get_object_or_404(PostPackage, pk=pk)
    package.is_active = True
    package.save()
    messages.success(request, 'Activated successfully')
    return redirect('package_list')


@login_required
def package_deactivate(request, pk):
    package = get_object_or_404(PostPackage, pk=pk)
    package.is_active = False
    package.save()
    messages.success(request, 'Deactivated successfully')
    return redirect('package_list')


@login_required
def packages(request):
    header = 'Packages'
    return render(request, "admin/package/list.html", {'header': header, })


def create_or_edit_item(request, model, form_class, template_name, pk=None):
    if pk:
        instance = get_object_or_404(model, pk=pk)
    else:
        instance = None

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('item_list')  # Change to your desired success URL
    else:
        form = form_class(instance=instance)

    return render(request, template_name, {'form': form})


def toggle_active_status(request, model, pk):
    item = get_object_or_404(model, pk=pk)
    item.is_active = not item.is_active
    item.save()
    return redirect('item_list')  # Change to your desired success URL


# Specific views for each model
def create_or_edit_post_package_detail(request, pk=None):
    return create_or_edit_item(request, PostPackageDetail, PostPackageDetailForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_package_feature(request, pk=None):
    return create_or_edit_item(request, PostPackageFeature, PostPackageFeatureForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_part(request, pk=None):
    return create_or_edit_item(request, PostPart, PostPartForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_charging(request, pk=None):
    return create_or_edit_item(request, PostCharging, PostChargingForm, 'admin/package/common_form.html', pk)


def create_or_edit_post_paint(request, pk=None):
    return create_or_edit_item(request, PostPaint, PostPaintForm, 'admin/package/common_form.html', pk)


def toggle_post_package_detail(request, pk):
    return toggle_active_status(request, PostPackageDetail, pk)


def toggle_post_package_feature(request, pk):
    return toggle_active_status(request, PostPackageFeature, pk)


def toggle_post_part(request, pk):
    return toggle_active_status(request, PostPart, pk)


def toggle_post_charging(request, pk):
    return toggle_active_status(request, PostCharging, pk)


def toggle_post_paint(request, pk):
    return toggle_active_status(request, PostPaint, pk)


def all_package_details(request, pk):
    package = PostPackage.objects.get(id=pk)
    package_details = PostPackageDetail.objects.filter(package=str(package.id))
    # package_features = PostPackageFeature.objects.all()
    # parts = PostPart.objects.all()
    # charging = PostCharging.objects.all()
    # paints = PostPaint.objects.all()

    context = {
        'package': package,
        'package_details': package_details,
        'package_features': 'package_features',
        'parts': 'parts',
        'charging': 'charging',
        'paints': 'paints'
    }
    return render(request, 'admin/package/details.html', context)

@login_required
def reserved_car_list(request):
    reserved_cars = PostPayment.objects.filter(status='succeeded').order_by('-created_at')
    return render(request, 'admin/reserved_cars/list.html', {'reserved_cars': reserved_cars})

@login_required
def community_member_list(request):
    header = 'Community Members'
    members = PostCommunityJoiners.objects.all().order_by('-created_at')
    return render(request, 'admin/community_members.html', {'members': members,'header':header})

@login_required
def subscriber_list(request):
    header = 'Subscribers'
    subscribers = PostSubscribers.objects.all().order_by('-created_at')
    return render(request, 'admin/subscribers.html', {'subscribers': subscribers,'header':header})







# car configurator page
@login_required
def save_car_configuration(request):
    """
    Save the car configuration from the form submission
    """
    if request.method == 'POST':
        try:
            # Get the car model
            slug = request.POST.get('car_slug')
            car_model_id = request.POST.get('car_model')
            # print("car model id is: ", car_model_id, "slug is: ", slug)
            car_model = get_object_or_404(PostNavItem, id=car_model_id)

            print("car model is: ", car_model.id)
            totalPrice = request.POST.get('total_price')

            print("TOtal price is: ", request.POST.get('total_price'))
            
            # Create a new configuration or update if exists
            config, created = CarConfiguration.objects.get_or_create(
                user=request.user,
                car_model=car_model,
                is_saved=True,
                defaults={
                    # Exterior options
                    'exterior_color': request.POST.get('exterior_color'),
                    'wheel_type': request.POST.get('wheel_type'),
                    'wheel_color': request.POST.get('wheel_color'),
                    'grille_style': request.POST.get('grille_style'),
                    'roof_type': request.POST.get('roof_type'),
                    'mirror_style': request.POST.get('mirror_style'),
                    'lighting_package': request.POST.get('lighting_package'),
                    'decals': request.POST.get('decals'),
                    
                    # Interior options
                    'upholstery_material': request.POST.get('upholstery_material'),
                    'interior_color': request.POST.get('interior_color'),
                    'seat_type': request.POST.get('seat_type'),
                    'dashboard_trim': request.POST.get('dashboard_trim'),
                    'steering_wheel': request.POST.get('steering_wheel'),
                    
                    # Performance options
                    'engine_type': request.POST.get('engine_type'),
                    'transmission': request.POST.get('transmission'),
                    'drivetrain': request.POST.get('drivetrain'),
                    'suspension': request.POST.get('suspension'),
                    'exhaust_system': request.POST.get('exhaust_system'),
                    
                    # Technology options
                    'infotainment_system': request.POST.get('infotainment_system'),
                    'sound_system': request.POST.get('sound_system'),
                    'heads_up_display': request.POST.get('heads_up_display') == 'true',
                    'connectivity_package': request.POST.get('connectivity_package'),
                    
                    # Safety options
                    'autonomous_driving_level': request.POST.get('autonomous_driving_level'),
                    'parking_assist': request.POST.get('parking_assist') == 'true',
                    'blind_spot_monitoring': request.POST.get('blind_spot_monitoring') == 'true',
                    'night_vision': request.POST.get('night_vision') == 'true',
                    
                    # Package options
                    'luxury_package': request.POST.get('luxury_package') == 'true',
                    'sport_package': request.POST.get('sport_package') == 'true',
                    'winter_package': request.POST.get('winter_package') == 'true',
                    'offroad_package': request.POST.get('offroad_package') == 'true',
                    'towing_hitch': request.POST.get('towing_hitch') == 'true',
                    'roof_rack': request.POST.get('roof_rack') == 'true',
                    
                    # Price information
                    'exterior_price': request.POST.get('exterior_price'),
                    'interior_price': request.POST.get('interior_price'),
                    'performance_price': request.POST.get('performance_price'),
                    'tech_price': request.POST.get('tech_price'),
                    'package_price': request.POST.get('package_price'),
                    'base_price': request.POST.get('base_price'),
                    'total_price': request.POST.get('total_price'),
                }
            )
            
            # If configuration already existed, update its fields
            if not created:
                # Update exterior options
                config.exterior_color = request.POST.get('exterior_color')
                config.wheel_type = request.POST.get('wheel_type')
                config.wheel_color = request.POST.get('wheel_color')
                config.grille_style = request.POST.get('grille_style')
                config.roof_type = request.POST.get('roof_type')
                config.mirror_style = request.POST.get('mirror_style')
                config.lighting_package = request.POST.get('lighting_package')
                config.decals = request.POST.get('decals')
                
                # Update interior options
                config.upholstery_material = request.POST.get('upholstery_material')
                config.interior_color = request.POST.get('interior_color')
                config.seat_type = request.POST.get('seat_type')
                config.dashboard_trim = request.POST.get('dashboard_trim')
                config.steering_wheel = request.POST.get('steering_wheel')
                
                # Update performance options
                config.engine_type = request.POST.get('engine_type')
                config.transmission = request.POST.get('transmission')
                config.drivetrain = request.POST.get('drivetrain')
                config.suspension = request.POST.get('suspension')
                config.exhaust_system = request.POST.get('exhaust_system')
                
                # Update technology options
                config.infotainment_system = request.POST.get('infotainment_system')
                config.sound_system = request.POST.get('sound_system')
                config.heads_up_display = request.POST.get('heads_up_display') == 'true'
                config.connectivity_package = request.POST.get('connectivity_package')
                
                # Update safety options
                config.autonomous_driving_level = request.POST.get('autonomous_driving_level')
                config.parking_assist = request.POST.get('parking_assist') == 'true'
                config.blind_spot_monitoring = request.POST.get('blind_spot_monitoring') == 'true'
                config.night_vision = request.POST.get('night_vision') == 'true'
                
                # Update package options
                config.luxury_package = request.POST.get('luxury_package') == 'true'
                config.sport_package = request.POST.get('sport_package') == 'true'
                config.winter_package = request.POST.get('winter_package') == 'true'
                config.offroad_package = request.POST.get('offroad_package') == 'true'
                config.towing_hitch = request.POST.get('towing_hitch') == 'true'
                config.roof_rack = request.POST.get('roof_rack') == 'true'
                
                # Update price information
                config.exterior_price = clean_price_value(request.POST.get('exterior_price'))
                config.interior_price = clean_price_value(request.POST.get('interior_price'))
                config.performance_price = clean_price_value(request.POST.get('performance_price'))
                config.tech_price =clean_price_value( request.POST.get('tech_price'))
                config.package_price = clean_price_value(request.POST.get('package_price'))
                config.base_price = clean_price_value(request.POST.get('base_price'))
                config.total_price = clean_price_value(totalPrice)
                
                config.save()
            
            messages.success(request, 'Your car configuration has been saved successfully!')
            return redirect('car_configuration_detail', config_id=config.id)
            # return redirect('view_configuration', config_id=config.id)
            
        except Exception as e:
            messages.error(request, f'Error saving configuration: {str(e)}')
            return redirect( 'car_configurator_slug',slug)
    
    # If not POST, redirect to car models
    return redirect('car_models')

def car_models(request):
    """
    Display available car models to configure
    """
    car_models = PostNavItem.objects.all()
    
    context = {
        'car_models': car_models
    }
    
    return render(request, 'public/car_models.html', context)

@login_required
def saved_configurations(request):
    """
    Display all saved configurations for the logged-in user
    """
    configurations = CarConfiguration.objects.filter(user=request.user, is_saved=True)
    
    context = {
        'configurations': configurations
    }
    
    return render(request, 'public/saved_configurations.html', context)

# @login_required
# def view_configuration(request, config_id):
#     """
#     View a specific saved configuration
#     """
#     configuration = get_object_or_404(CarConfiguration, id=config_id, user=request.user)
    
#     context = {
#         'config': configuration,
#         'items': configuration.car_model,
#         'amount_due': configuration.total_price,
        
#     }
    
#     return render(request, 'public/view_configuration.html', context)




# new configurations system


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_booked_packages(request):
    """
    Get all booked packages
    """
    packages = BookedPackage.objects.all()
    serializer = BookedPackageSerializer(packages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booked_package_by_id(request, pk):
    """
    Get a booked package by ID
    """
    print("****~~~~~****~~~~~GOOT ID",pk)
    try:
        package = BookedPackage.objects.get(pk=pk)
        serializer = BookedPackageSerializer(package)
        return Response(serializer.data)
    except BookedPackage.DoesNotExist:
        return Response(
            {"error": "Booked package not found"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booked_packages_by_user_id(request, user_id):
    """
    Get all booked packages for a specific user
    """
    packages = BookedPackage.objects.filter(user_id=user_id)
    serializer = BookedPackageSerializer(packages, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_booked_package(request):
    """
    Create a new booked package
    """
    data = request.data.copy() 
    data['user'] = request.user.id
    serializer = BookedPackageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_booked_package(request, pk):
    """
    Update an existing booked package
    """
    try:
        package = BookedPackage.objects.get(pk=pk)
    except BookedPackage.DoesNotExist:
        return Response(
            {"error": "Booked package not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = BookedPackageSerializer(package, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_booked_package(request, pk):
    """
    Delete a booked package
    """
    try:
        package = BookedPackage.objects.get(pk=pk)
        package.delete()
        return Response({"message": "Booked package deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except BookedPackage.DoesNotExist:
        return Response(
            {"error": "Booked package not found"},
            status=status.HTTP_404_NOT_FOUND
        )
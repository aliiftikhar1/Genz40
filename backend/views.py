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
from .models import PostCommunity, PostPackageDetail, PostPackageFeature, PostPart, PostCharging, PostPaint
from .forms import CustomPasswordResetForm, CustomPasswordResetConfirmForm, PostPackageDetailForm, PostPackageFeatureForm, PostPartForm, PostChargingForm, PostPaintForm, \
    ImageModelForm
from .forms import RegisterForm, PostPackageForm, PostNavItemForm
from .models import PostPackage, PostNavItem
import string
import random
from common.utils import get_client_ip, send_custom_email
import requests


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
    # ip = get_country_info(request)
    ip = "103.135.189.223"
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
        # ip = '103.135.189.214'
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
def package_list(request):
    all_package_list = PostPackage.objects.all()
    return render(request, 'admin/package/list.html', {'packages': all_package_list})


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
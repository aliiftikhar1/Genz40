import json
import re
import uuid
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from common.utils import EmailThread, get_client_ip
from django.templatetags.static import static
from .forms import PostContactForm, RegisterForm
from backend.models import CarConfiguration, BookedPackage , CustomUser, PostCommunity, PostCommunityJoiners, PostContactUs, PostNavItem, PostLandingPageImages, PostPackage, PostPayment, PostSubscribers
from django.contrib import messages
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from frontend.forms import PostSubscribeForm
from django.urls import path
from django.views import View
from django.urls import reverse
from backend.models import BookedPackage, ReservationNewFeatures, ReservationFeaturesPayment, DynamicPackages, FeaturesSection, PackageFeatureRoller, PackageFeatureRollerPlus, PackageFeatureBuilder
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator
import string
import random
from django.contrib.auth import login
from django.http import JsonResponse
import time  
import requests
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import HttpResponse
import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str 
from .tokens import account_activation_token
from common.utils import send_otp, verify_otp
from django.core.cache import cache
from decimal import Decimal
from django.db.models import Sum


stripe.api_key = settings.STRIPE_SECRET_KEY

MAILCHIMP_API_URL = f"https://{settings.MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0"

User = get_user_model()

def get_country_info(request):
    ip = get_client_ip(request)
    # response = requests.get(f'http://api.ipstack.com/{ip}?access_key={settings.IPSTACK_API_KEY}')
    # data = response.json()
    # country_code = data.get('country_code')
    return ip

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)
    items = PostNavItem.objects.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    context = {
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'section_1': section_1,
        'section_2': section_2,
        'section_3': section_3,
        'random_password': random_password,
        'items': items
    }

    return render(request, 'public/index.html', context)

def home(request):
    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)
    items = PostNavItem.objects.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    context = {
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'section_1': section_1,
        'section_2': section_2,
        'section_3': section_3,
        'random_password': random_password,
        'items': items
    }

    return render(request, 'public/index.html', context)

def tech_specs(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    context = {
        'items': items,
        'package_details': package_details
    }
    return render(request, 'public/technical_specs.html', context)


def learn_more(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    allitems = PostNavItem.objects.all()  
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    
    # Use the static() function to generate URLs for static files
    markI_images = [
        {"id": 1, "url": static('images/car/Mark-I/car-1.png')},
        {"id": 2, "url": static('images/car/Mark-I/car-1.png')},
        {"id": 3, "url": static('images/car/Mark-I/car-1.png')},
        {"id": 4, "url": static('images/car/Mark-I/car-1.png')},
        {"id": 5, "url": static('images/car/Mark-I/car-1.png')},
    ]
    markII_images = [
        {"id": 1, "url": static('images/car/Mark-II/car-2.png')},
        {"id": 2, "url": static('images/car/Mark-II/car-2.png')},
        {"id": 3, "url": static('images/car/Mark-II/car-2.png')},
        {"id": 4, "url": static('images/car/Mark-II/car-2.png')},
        {"id": 5, "url": static('images/car/Mark-II/car-2.png')},
    ]
    markIV_images = [
        {"id": 1, "url": static('images/car/Mark-IV/car-3.png')},
        {"id": 2, "url": static('images/car/Mark-IV/car-3.png')},
        {"id": 3, "url": static('images/car/Mark-IV/car-3.png')},
        {"id": 4, "url": static('images/car/Mark-IV/car-3.png')},
        {"id": 5, "url": static('images/car/Mark-IV/car-3.png')},
    ]
    
    Images = []
    if slug == 'Mark-I':
        Images = markI_images
    elif slug == 'Mark-II':
        Images = markII_images
    elif slug == 'Mark-IV':
        Images = markIV_images
    
    context = {
        'allitems': allitems,
        'items': items,
        'package_details': package_details,
        'Images': Images,
    }
    
    return render(request, 'public/LearnMore.html', context)

def about(request):
    return render(request, 'public/about.html', {
        'navbar_style': 'dark'
    })

def blog(request):
    # items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/blog.html', {
        'navbar_style': 'dark'
    })

def blog_details(request):
    # items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/blog_details.html', {
        'navbar_style': 'dark',
        # 'details': items
    })

def contact_us(request):
    return render(request, 'public/contact_us.html')

def terms_conditions(request):
    return render(request, 'public/terms_conditions.html')

def privacy_policy(request):
    return render(request, 'public/privacy_policy.html')

def subscribe_email(email):
    """Subscribe an email to Mailchimp Audience List."""
    url = f"{MAILCHIMP_API_URL}/lists/{settings.MAILCHIMP_LIST_ID}/members/"
    data = {
        "email_address": email,
        "status": "subscribed"  # Can be "pending" for double opt-in
    }
    headers = {
        "Authorization": f"apikey {settings.MAILCHIMP_API_KEY}"
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return {"message": "Successfully subscribed!"}
    else:
        return response.json()  # Return Mailchimp's error response
    
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def register_page(request):
    form = RegisterForm()
    random_password = generate_random_password()
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    context = {
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'random_password': random_password,
        'form': form
    }
    return render(request, 'registration/register.html', context)

def send_activation_email(request, user, random_password):
    current_site = get_current_site(request)
    subject = "Activate Your Account"
    print("User Details before sending activation email",current_site,user,random_password)
    html_content = render_to_string("email/activation_email.html", {
        "email": user.email,
        "password": random_password,
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    })
    
    plain_text = strip_tags(html_content)
    sender = settings.EMAIL_FROM
    recipient_list = [user.email]
    EmailThread(subject, html_content, recipient_list, sender).start()

# def send_activation_email(request, user, random_password):
   
#     current_site = get_current_site(request)
#     mail_subject = "Activate Your Account"
#     print("User Details before sending activation email",current_site,user,random_password)
#     html_message = render_to_string("email/activation_email.html", {
#         "email": user.email,
#         "password": random_password,
#         "user": user,
#         # "domain": 'http://178.128.150.238',
#         "domain": current_site.domain,
#         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#         "token": account_activation_token.make_token(user),
#     })
    
#     plain_message = strip_tags(html_message)
    
#     # Send mail with both HTML and plain text versions
#     send_mail(
#         subject=mail_subject,
#         message=plain_message,  # Plain text version
#         from_email=settings.EMAIL_FROM,
#         recipient_list=[user.email],
#         html_message=html_message  # HTML version
    # )

def get_register_community(request):
    if request.method == 'POST':
        user = CustomUser.objects.filter(email=request.POST['email']).exists()
        if not user:
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                # random_password = generate_random_password()
                user.set_password(request.POST['password1'])
                user.is_active = True
                user.save()
                PostCommunityJoiners.objects.create(user=user)
                return JsonResponse({"message": "Thank You for Joining. This Feature is currently under progress and you will be automatically added in our community once it's developed.", 'is_success': True})       
        else:
            user = CustomUser.objects.get(email=request.POST['email'])
            if not PostCommunityJoiners.objects.filter(user=user.id).exists():
                PostCommunityJoiners.objects.create(user=user)
                return JsonResponse({"message": 'Successfully added.', 'is_success': True})
            else:
                return JsonResponse({"message": 'Already joined.', 'is_success': False})

def get_register(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone_number = request.POST['phone_number']

        # Check if a user already exists with the same email or phone number
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"message": "This email is already registered!", 'is_success': False})

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({"message": "This phone number is already registered!", 'is_success': False})

        if not CustomUser.objects.filter(email=request.POST['email'], phone_number=request.POST['phone_number']).exists():
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(request.POST['password1'])
                user.is_active = True
                # user.is_email_verified = True
                
                # Format phone number to match the expected format (removing non-digit characters)
                if user.phone_number:
                    # Extract only digits from the phone number
                    digits_only = ''.join(filter(str.isdigit, user.phone_number))
                    # Ensure it's no longer than 14 digits as per your model validation
                    user.phone_number = digits_only[:14]
                
                # Check if zip_code is present and ensure it's within the 5-character limit
                if hasattr(user, 'zip_code') and user.zip_code and len(user.zip_code) > 5:
                    user.zip_code = user.zip_code[:5]
                
                try:
                    print("User data before saving:", user.__dict__)
                    user.save()
                    
                    # Email sending logic
                    subject = "Welcome to Our Platform - www.genz40.com"
                    recipient_list = [user.email]
                    sender = settings.EMAIL_FROM
                    html_content = render_to_string("email/welcome_email.html", {'user': user, 'password': request.POST['password1']})
                    send_activation_email(request, user, request.POST['password1'])
                    # EmailThread(subject, html_content, recipient_list, sender).start()
                    
                    return JsonResponse({"message": 'Successfully added. Please check mailbox for password.', 'is_success': True})
                except Exception as e:
                    # Log the error for debugging
                    print(f"Error saving user: {str(e)}")
                    return JsonResponse({"message": f'Registration failed: {str(e)}', 'is_success': False})
            else:
                # Form validation errors
                errors = form.errors.as_json()
                return JsonResponse({"message": f'Invalid form data: {errors}', 'is_success': False})
        else:
            return JsonResponse({"message": 'Already joined.', 'is_success': False})
    
    # If not POST method
    else:
        register_page(request)

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        # return JsonResponse({"message": 'Your account has been activated successfully!'})
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('customer_login')
    else:
        messages.error(request, 'Invalid activation link!')
        return redirect('customer_login')
        # return JsonResponse({"message": 'Invalid activation link!'})
    
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({"message": 'Login successfully.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Invalid username or password.', 'is_success': False})
    else:
        return render(request, 'registration/login.html')
  
def subscribe(request):
    if request.method == 'POST':
        subscribe_email(request.POST['email'])
        if not PostSubscribers.objects.filter(email=request.POST['email']).exists():
            form = PostSubscribeForm(request.POST)
            if form.is_valid():
                form.save()
                subscribe_email(request.POST['email'])
                subject = 'Thank you for Newsletter subscribe - www.genz40.com'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [settings.ADMIN_EMAIL]
                c = {'name': 'Salman'}
                html_content = render_to_string('email/subscribe_user.html', c)
                send_mail(subject, html_content, email_from, recipient_list, fail_silently=False,
                            html_message=html_content)
                return JsonResponse({"message": 'Successfully subscribed.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Already subscribed.', 'is_success': False})

def navitem_detail(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package = items.details.filter(is_active=True).order_by('position')
    return render(request, 'public/navitem_detail.html',
                  {'items': items,
                   'packages': package})

def car_configurator(request,slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    # configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id),car_model_id=items.id)
    amount_due = package_details[0].amount_due
    # print("**********----*****Existing Configurations are : ",configure_vehicles)
    return render(request, 'public/CarConfigurator.html', {'items': items,
                                                        #    'existing_configurations':configure_vehicles,
                                                           'packages': package_details,
                                                           'amount_due': amount_due,
                                                           'slug': slug})

def new_car_configurator(request,slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    # configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id),car_model_id=items.id)
    amount_due = package_details[0].amount_due
    random_password = generate_random_password()
    # print("**********----*****Existing Configurations are : ",configure_vehicles)
    return render(request, 'public/Car-Configurator/MainFile.html', {'items': items,
                                                        #    'existing_configurations':configure_vehicles,
                                                           'packages': package_details,
                                                           'random_password':random_password,
                                                           'amount_due': amount_due,
                                                           'slug': slug})
    
def car_details(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    print('---------package', package_details[0].amount_due)
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    return render(request, 'public/car_details.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password})

def reserve_now(request, slug):
    email = request.GET.get('email', '')
    if not PostSubscribers.objects.filter(email=email).exists():
        PostSubscribers.objects.create(email=email)
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    return render(request, 'public/reserve_now.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password,
                    'email': email})

def lock_your_price_now(request, slug):
    email = request.GET.get('email', '')
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    return render(request, 'public/lock_your_price_now.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password,
                    'email': email})

def reserve_configuration_now(request, slug):
    email = request.GET.get('email', '')
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    random_password = generate_random_password()
    ip = get_country_info(request)
    # ip = "103.135.189.223"
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
    return render(request, 'public/lock_your_price_now.html',
                  {'items': items,
                   'packages': package_details,
                   'amount_due': amount_due,
                   'country_code': country_code,
                    'country_flag_url': country_flag_url,
                    'random_password': random_password,
                    'email': email})


def save_contact(request):
    if request.method == 'POST':
        mail_subject = "Thank you for contacting us"
        context = {
        'admin': 'Salman',
        'name': request.POST['name'],
        'email': request.POST['email'],
        'phone_number': request.POST['phone_number'],
        'car': request.POST['car'],
        'comments': request.POST['comments']
        }
        html_content = render_to_string("email/contact_admin.html", context)  # HTML content
        plain_text = strip_tags(html_content) 

        send_mail(
        subject=mail_subject,
        message=plain_text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_content, 
         )
        if not PostContactUs.objects.filter(email=request.POST['email']).exists():
            form = PostContactForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
            else:
                return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
        
def generate_reference_number():
    # Get today's date in MMDDYY format
    today_date = datetime.datetime.today().strftime('%m%d%y')
    # Get the last inserted number from the database
    last_entry = PostPayment.objects.order_by('-created_at').first()  # Get last record
    last_number = int(last_entry.rn_number[-4:]) if last_entry else 1004  # Start from 1000 if no entry exists
    # Increment the last number
    new_number = last_number + 1
    # Generate the new reference number
    reference_number = f"RN{today_date}{new_number:04d}"  # Ensures 4-digit number format
    return reference_number

def create_account_before_checkout(request):
    if request.method == 'POST':
        new_ref = generate_reference_number()
        amount = request.POST['amount']  # Amount in cents (e.g., $50.00)
        product_name = request.POST['package']
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email, phone_number=request.POST['phone_number']).first()
        if user:
            # Both email and phone exist in the same account → Proceed further
            login(request, user)
            fullName = user.first_name+ ' '+user.last_name
            session_data = {'product_name': product_name, 'amount': amount, 
                                    'email':user.email, 'fullName':fullName, 'id':user.id, 'new_ref':new_ref}
            # Ensure session_data is returned as a JSON response
            return JsonResponse({"message": "Success.", 'is_success': True, 'session_data': session_data})
                        
        # Check if a user already exists with the same email or phone number
        email_exists = CustomUser.objects.filter(email=email).exists()
        phone_exists = CustomUser.objects.filter(phone_number=request.POST['phone_number']).exists()

        if email_exists and phone_exists:
            return JsonResponse({"message": "This email and phone number belong to different users.", 'is_success': False})
        elif email_exists:
            return JsonResponse({"message": "This email is already registered.", 'is_success': False})
        elif phone_exists:
            return JsonResponse({"message": "This phone number is already registered.", 'is_success': False})
        else:
            print('-----not')
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(request.POST['password1'])
                user.zip_code = request.POST['zip_code']
                user.save()
                # user = form.get_user()
                login(request, user)
                subject = "Welcome to Our Platform - www.genz40.com"
                recipient_list = [user.email]
                sender = settings.EMAIL_FROM  # Ensure this is set in settings.py
                # Render HTML email template
                html_content = render_to_string("email/welcome_email.html", {'user': user, 'password': request.POST['password1']})
                # Send email in background
                EmailThread(subject, html_content, recipient_list, sender).start()

                if(user.id):
                    fullName = user.first_name+ ' '+user.last_name
                    session_data = {'product_name': product_name, 'amount': amount, 
                                    'email':user.email, 'fullName':fullName, 'id':user.id, 'new_ref':new_ref}
                    return JsonResponse({"message": "Success.", 'is_success': True, 'session_data': session_data})

def create_checkout_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
            email = data.get("email")
            product_name = data.get("product_name")
            amount = data.get("amount")
            full_name = data.get("full_name")
            user_id = data.get("id")
            new_ref = data.get("new_ref")

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': "usd",
                        'product_data': {
                            'name': product_name,
                            'description': 'This reservation will save your position in line. When you car is available for production, we will invite you to configure and choose from dozens of options to make it complete personalized and unique.',
                            'images': ['https://genz40.com/static/images/genz/mark1-builder4.png'],
                        },
                        'unit_amount': int(amount) * 100,  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://genz40.com/success/',
                cancel_url='https://genz40.com/cancel/',
                customer_email=email,
                metadata={
                    'full_name': full_name,
                    'email': email,
                    'new_ref': new_ref,
                    'product_name': product_name,
                    'description': str(user_id), #Passing Userid
                },
                payment_intent_data={
                'description': str(user_id), #Passing Userid
                "metadata": {
                    'new_ref':new_ref,
                    'product_name': product_name
                },
                },
            )
            return JsonResponse({"is_success": True, "checkout_url": session.url})
        except Exception as e:
            return JsonResponse({"is_success": False, "message": str(e)})

    return JsonResponse({"is_success": False, "message": "Invalid request"})

def payment_success(request):
    return render(request, 'public/payment/success.html', {'is_footer_required': False})

def payment_cancel(request):
    return render(request, 'public/payment/cancel.html', {'is_footer_required': False})

# STRIPE_WEBHOOK_KEY= 'whsec_559bd2071b3e1bf765d4ad825586dcaab38522c998fcccd802bc40f1d90f84c9'

@csrf_exempt  # Webhooks don't require CSRF protection
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_KEY
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.created':
        payment_intent = event['data']['object']
        # getting user id
        user_id = payment_intent.get('description')
        user_uuid = uuid.UUID(user_id)
        PostPayment.objects.create(
            user_id=user_uuid,
            package_name=payment_intent['metadata']['product_name'],
            stripe_payment_id=payment_intent['id'],
            amount='100',  # Convert to dollars
            rn_number=payment_intent['metadata']['new_ref'], #RN0130251005
            currency='usd',
            status='created',
        )
    elif event['type'] == 'charge.updated':
        payment_intent = event['data']['object']
        payment = PostPayment.objects.get(stripe_payment_id=payment_intent['payment_intent'])
        payment.status = payment_intent['status']
        payment.save()

        mail_subject = "New car reserved - GEN-Z 40"
        context = {
        'admin': 'Salman'
        }
        html_content = render_to_string("email/contact_admin.html", context)  # HTML content
        plain_text = strip_tags(html_content) 
        send_mail(
        subject=mail_subject,
        message=plain_text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_content, 
         )
    elif event['type'] == 'payment_intent.succeeded':
        print('=======================')
    else:
        print(f"Unhandled event type: {event['type']}")

    return JsonResponse({'success': True})

@login_required
def dashboard(request):
    header = 'Dashboard'
    print('-request.user.role', request.user.role)
    if request.user.role == 'admin':
        return render(request, "admin/dashboard.html", {'header': header })
    elif request.user.role == 'customer':
        return redirect('my_vehicles')
        # return render(request, "customer/dashboard.html", {'header': header })
    else:
        section_1 = get_object_or_404(PostLandingPageImages, section=1)
        section_2 = get_object_or_404(PostLandingPageImages, section=2)
        section_3 = get_object_or_404(PostLandingPageImages, section=3)
        random_password = generate_random_password()
        ip = get_country_info(request)
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        country_code = data.get('country')
        # country_flag_url = f'https://www.countryflags.io/{country_code}/flat/64.png'
        country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'
        context = {
            'country_code': country_code,
            'country_flag_url': country_flag_url,
            'section_1': section_1,
            'section_2': section_2,
            'section_3': section_3,
            'random_password': random_password
        }

        return render(request, 'public/index.html', context)
        # return render(request, "customer/dashboard.html", {'header': header })
        # return redirect('index')
  
@login_required
def my_vehicles(request):
    order_vehicles = PostPackage.objects.filter(is_active=True).order_by('position')
    vehicles = PostNavItem.objects.filter(is_active=True).order_by('position')
    configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id))
    booked_packages = BookedPackage.objects.filter(user=str(request.user.id)).exclude(status='cancelled')
    print('-----configure_vehicles', configure_vehicles)
    # amount_due = order_vehicles[0].amount_due
    context = {
        'configure_vehicles':configure_vehicles,
        'order_vehicles': order_vehicles,
        'vehicles': vehicles,
        'booked_packages': booked_packages
    }
    return render(request, 'customer/reserved_vehicles/my_vehicles.html', context, {'is_footer_required': True})


@login_required
def my_configurations(request):
    reserverd_vehicles = PostPayment.objects.filter(user_id=str(request.user.id), status='succeeded')
    order_vehicles = PostPackage.objects.filter(is_active=True).order_by('position')
    vehicles = PostNavItem.objects.filter(is_active=True).order_by('position')
    configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id))
    print('-----configure_vehicles', configure_vehicles)
    # amount_due = order_vehicles[0].amount_due
    context = {
        'configure_vehicles':configure_vehicles,
        'reserverd_vehicles':reserverd_vehicles,
        'order_vehicles': order_vehicles,
        'vehicles': vehicles
    }
    return render(request, 'customer/reserved_vehicles/my_configurations.html', context, {'is_footer_required': True})
@login_required
def my_package_bookings(request):
    reserverd_vehicles = PostPayment.objects.filter(user_id=str(request.user.id), status='succeeded')
    order_vehicles = PostPackage.objects.filter(is_active=True).order_by('position')
    vehicles = PostNavItem.objects.filter(is_active=True).order_by('position')
    configure_vehicles = CarConfiguration.objects.filter(user_id=str(request.user.id))
    booked_packages = BookedPackage.objects.filter(user=str(request.user.id))
    
    context = {
        'configure_vehicles':configure_vehicles,
        'reserverd_vehicles':reserverd_vehicles,
        'order_vehicles': order_vehicles,
        'vehicles': vehicles,
        'booked_packages': booked_packages
    }
    return render(request, 'customer/reserved_vehicles/my_package_bookings.html', context, {'is_footer_required': True})


@login_required
def my_vehicle_details(request, id):
    reserverd_vehicle = PostPayment.objects.get(id=id)
    context = {
        'reserverd_vehicle':reserverd_vehicle
    }
    return render(request, 'customer/reserved_vehicles/vehicle_details.html', context, {'is_footer_required': True})

@login_required
def payment_history(request):
    # Get successful reservation payments for the current user
    reservation_payments = PostPayment.objects.filter( user=request.user, status='succeeded' ).select_related('rn_number').order_by('-created_at')
    
    # Get successful feature payments for the current user
    new_feature_payments = ReservationFeaturesPayment.objects.filter(
         reservation_feature__booked_package__user=request.user, payment_status='completed' 
    ).select_related(
        'reservation_feature',
        'reservation_feature__booked_package'
    ).order_by('-payment_date')
    
    context = {
        'reservation_payments': reservation_payments,
        'new_feature_payments': new_feature_payments,
        'is_footer_required': True
    }
    return render(request, 'customer/reserved_vehicles/payments.html', context)

@login_required
def profile_settings(request):
    return render(request, 'customer/profile/profile_settings.html', {'is_footer_required': True})

@login_required
def customer_message(request):
    return render(request, 'customer/message/message.html', {'is_footer_required': True})

@login_required
def email_verify_from_dashboard(request):
    if request.user.is_authenticated:
        current_site = get_current_site(request)
        mail_subject = "Activate Your Account"
        context = {
            "user": request.user.first_name +' '+ request.user.last_name,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(request.user.pk)),
            "token": account_activation_token.make_token(request.user),
        }
        
        html_content = render_to_string("email/send_email_verification.html", context)  # HTML content
        plain_text = strip_tags(html_content) 

        send_mail(
        subject=mail_subject,
        message=plain_text,
        from_email=settings.EMAIL_FROM,
        recipient_list=[request.user.email],
        html_message=html_content, 
    )
        return JsonResponse({"is_success": True, "message": "Activation mail sent successfully."})
    else:
        return JsonResponse({"is_success": False, "message": "Failed to sent. Please try again."})

def clean_phone_number(phone_number):
    """Removes all non-numeric characters from a phone number."""
    return re.sub(r"\D", "", phone_number)
                  
@login_required
def send_otp_view(request):
    """Send OTP to the phone number"""
    user = get_object_or_404(User, id=request.user.id)
    phone_number = user.phone_number
    if not phone_number:
        return JsonResponse({"message": "Phone number is required", "is_success": False})

     # Check OTP request count
    cache_key = f"otp_attempts_{phone_number}"
    attempts = cache.get(cache_key, 0)

    if attempts >= settings.OTP_REQUEST_LIMIT:
        return JsonResponse({"message": "Too many OTP requests. Try again later.", "is_success": False})

    cleaned_number = clean_phone_number(phone_number)
    
    # Fetch country dialing code using an external API
    phone_response = requests.get(f"https://restcountries.com/v3.1/alpha/{user.country}")
    phone_data = phone_response.json()
    
    if phone_data:
        cleaned_number = f"{phone_data[0]['idd']['root']}"+cleaned_number
        # Send OTP using Twilio
        status_otp = send_otp(cleaned_number)

        # Update request count
        cache.set(cache_key, attempts + 1, settings.OTP_TIME_WINDOW)

        return JsonResponse({"message": "OTP sent", "status": status_otp, "is_success": True})

def otp_verify_page(request):
    return render(request, "customer/otp_verification.html")

@login_required
def verify_otp_view(request):
    """Verify the OTP entered by the user"""
    user = get_object_or_404(User, id=request.user.id)
    phone_number = user.phone_number
    if not phone_number:
        return JsonResponse({"message": "Phone number is required", "is_success": False})

    cleaned_number = clean_phone_number(phone_number)
    # Fetch country dialing code using an external API
    phone_response = requests.get(f"https://restcountries.com/v3.1/alpha/{user.country}")
    phone_data = phone_response.json()
    
    if phone_data:
        cleaned_number = f"{phone_data[0]['idd']['root']}"+cleaned_number
        data = json.loads(request.body)  # Parse JSON request body
        otp_code = data.get("otp")
        if not cleaned_number or not otp_code:
            return JsonResponse({"message": "Phone number and OTP are required", "is_success": False})

        # Verify OTP
        status_otp = verify_otp(cleaned_number, otp_code)
        if status_otp == "approved":
            user = get_object_or_404(User, phone_number=phone_number)
            user.is_phone_number_verified = True
            user.save()
            return JsonResponse({"message": "Phone number verified", "is_success": True})

    return JsonResponse({"message": "Invalid OTP", "is_success": False})

def car_selector(request):
    return render(request, "public/car_selector.html")  # Ensure this matches your template name


@login_required
def view_configuration(request, config_id):
    """
    View a specific saved configuration
    """
    configuration = get_object_or_404(CarConfiguration, id=config_id, user=request.user)
    slug = configuration.car_model.slug if hasattr(configuration.car_model, 'slug') else None
    
    context = {
        'configuration': configuration,
        'car_model': configuration.car_model,
        'config_id': config_id,
        'amount_due': configuration.total_price,
        'slug': slug  # Add the slug to the context
    }
    
    return render(request, 'public/view_configuration.html', context)


@login_required
def checkout(request):
    """
    View a cheout out page
    """
    return render(request, 'public/payment/checkout.html')


@login_required
def reservation_checkout(request, id):
    """
    View the reservation checkout page.
    """
    booked_package = get_object_or_404(BookedPackage, id=id)
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    context = {
        'user_details': request.user,
        'booked_package': booked_package,  # singular for clarity
        'country_code': country_code,
        'country_flag_url': country_flag_url,
    }

    return render(request, 'public/payment/reservation_checkout.html', context)



@csrf_exempt
def process_reservation_payment(request):
    if request.method == 'POST':
        try:
            user_id = request.user.id
            first_name = request.user.first_name
            last_name = request.user.last_name
            email = request.user.email
            phone_number = request.user.phone_number
            package_id = request.POST.get('package_id')

            print("User Id is : ",str(user_id))

            try:
                custom_user = CustomUser.objects.get(id=user_id)
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'})

            booked_package = BookedPackage.objects.get(id=package_id)
            
            customer = stripe.Customer.create(
                email=email,
                name=f"{first_name} {last_name}",
                phone=phone_number,
                metadata={
                    'package_id': str(package_id),
                    'user_email': email,
                }
            )

            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': booked_package.car_model.title,
                        'description': f"Payment for {booked_package.title} Package of {booked_package.car_model.title}",
                        'images': ['https://genz40.com/static/images/genz/mark1-builder4.png'],
                    },
                    'unit_amount': int(float(100) * 100),  # amount in cents
                },
                'quantity': 1,
            }]

            session_data = {
                'customer_id': customer.id,
                'line_items': line_items,
                'package_id': str(package_id),
                'success_url': request.build_absolute_uri(f'/car/reservation_success/{package_id}/'),
                'cancel_url': request.build_absolute_uri(f'/car/reservation-checkout/{package_id}/'),
                'metadata': {
                    'product_name':booked_package.car_model.title,
                    'package_id': str(package_id),
                    'user_email': email,
                    'descripton':f" Payment for {booked_package.title} Package of {booked_package.car_model.title}"
                },
                'payment_intent_data':{
                'description': f" Payment for {booked_package.title} Package of {booked_package.car_model.title}",
                "metadata": {
                    'product_name':booked_package.car_model.title, 
                },
                },
            }

            return JsonResponse({
                'is_success': True,
                'session_data': session_data,
                'message': 'Payment session prepared successfully'
            })

        except BookedPackage.DoesNotExist:
            return JsonResponse({
                'is_success': False,
                'message': 'Package not found'
            }, status=404)
        
        except Exception as e:
            return JsonResponse({
                'is_success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'is_success': False,
        'message': 'Invalid request method'
    }, status=405)




@csrf_exempt
def create_package_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                customer=data['customer_id'],
                payment_method_types=['card'],
                line_items=data['line_items'],
                mode='payment',
                success_url=f"{data['success_url']}{{CHECKOUT_SESSION_ID}}",
                cancel_url=data['cancel_url'],
                metadata=data['metadata'],
                payment_intent_data=data['payment_intent_data']
            )
            
            return JsonResponse({
                'is_success': True,
                'checkout_url': session.url,
                'message': 'Checkout session created successfully'
            })

        except Exception as e:
            return JsonResponse({
                'is_success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'is_success': False,
        'message': 'Invalid request method'
    }, status=405)



def reservation_success(request, id, sessionId):
    try:
        booked_package = BookedPackage.objects.get(id=id)
        remaining_payment_after_reserve = booked_package.price - Decimal('100.00')
        booked_package.status = 'confirmed'
        booked_package.build_status = 'payment_done'
        booked_package.remaining_price = remaining_payment_after_reserve
        booked_package.save()

        if sessionId:
            session = stripe.checkout.Session.retrieve(sessionId)
            print("Session Response is : ", session)
            
            booked_package_instance = BookedPackage.objects.get(reservation_number=booked_package.reservation_number)
            PostPayment.objects.create(
                user=booked_package.user,  
                rn_number=booked_package_instance,  
                stripe_payment_id=session.payment_intent,
                amount=100,  
                regarding="reserve",
                currency="usd",
                status="succeeded",  
                package_name=booked_package.title,
            )
        subject = "Reservation Confirmation - GEN-Z 40"
        current_site = get_current_site(request)
        context = {
                'user': request.user,
                'booked_package': booked_package,
                'amount': 100,  # Convert to string for template
                'payment_date': booked_package.updated_at,
                'domain': current_site.domain,
                'reservation_number': booked_package.reservation_number,
            }
        html_content = render_to_string('email/payment_successful.html', context)

        plain_text = strip_tags(html_content)
        receipient_list = [booked_package.user.email, settings.ADMIN_EMAIL]
        sender = settings.EMAIL_FROM
        
        EmailThread(subject, html_content, receipient_list, sender).start()
        return render(request, 'public/payment/success.html', {'is_footer_required': False})
    
    except Exception as e:
        print(f"Error in reservation_success: {str(e)}")
        return render(request, 'public/payment/error.html', {'error': str(e), 'is_footer_required': False})



RESERVATION_FEATURE_OPTIONS = [
    # Interior upgrades
    {
        'category': 'Interior',
        'name': 'Premium Leather Seats',
        'description': 'Upgrade to high-quality leather seats with custom stitching',
        'estimated_amount': 2500.00,
    },
    {
        'category': 'Interior',
        'name': 'Custom Dashboard',
        'description': 'Bespoke dashboard with premium materials and custom finishes',
        'estimated_amount': 1800.00,
    },
    {
        'category': 'Interior',
        'name': 'Advanced Entertainment System',
        'description': 'High-end audio system with additional speakers and subwoofer',
        'estimated_amount': 3200.00,
    },
    {
        'category': 'Interior',
        'name': 'Ambient Lighting Package',
        'description': 'Customizable interior LED lighting with multiple color options',
        'estimated_amount': 950.00,
    },
    
    # Exterior upgrades
    {
        'category': 'Exterior',
        'name': 'Custom Paint Job',
        'description': 'Premium paint with custom color matching and metallic finish',
        'estimated_amount': 3500.00,
    },
    {
        'category': 'Exterior',
        'name': 'Carbon Fiber Package',
        'description': 'Carbon fiber hood, mirrors, and trim elements',
        'estimated_amount': 4200.00,
    },
    {
        'category': 'Exterior',
        'name': 'Custom Wheels',
        'description': 'Premium alloy wheels with custom design and finish',
        'estimated_amount': 2800.00,
    },
    {
        'category': 'Exterior',
        'name': 'Enhanced Lighting Package',
        'description': 'LED headlights, taillights and additional lighting elements',
        'estimated_amount': 1600.00,
    },
    
    # Performance upgrades
    {
        'category': 'Performance',
        'name': 'Performance Exhaust System',
        'description': 'Custom exhaust system with improved flow and sound',
        'estimated_amount': 2200.00,
    },
    {
        'category': 'Performance',
        'name': 'Suspension Upgrade',
        'description': 'Enhanced suspension system with adjustable settings',
        'estimated_amount': 3800.00,
    },
    {
        'category': 'Performance',
        'name': 'Brake System Upgrade',
        'description': 'High-performance brake calipers, rotors and pads',
        'estimated_amount': 3200.00,
    },
    {
        'category': 'Performance',
        'name': 'Engine Tuning',
        'description': 'Custom engine calibration for improved performance',
        'estimated_amount': 1800.00,
    },
    
    # Technology upgrades
    {
        'category': 'Technology',
        'name': 'Advanced Driver Assistance',
        'description': 'Additional sensors and camera systems for enhanced safety',
        'estimated_amount': 2600.00,
    },
    {
        'category': 'Technology',
        'name': 'Digital Dash Upgrade',
        'description': 'Fully customizable digital instrument cluster',
        'estimated_amount': 1900.00,
    },
    {
        'category': 'Technology',
        'name': 'Remote Management System',
        'description': 'Enhanced connectivity with smartphone app integration',
        'estimated_amount': 1400.00,
    },
    {
        'category': 'Technology',
        'name': 'Advanced Navigation System',
        'description': 'Premium navigation with real-time updates and advanced routing',
        'estimated_amount': 1200.00,
    },
    
    # Comfort upgrades
    {
        'category': 'Comfort',
        'name': 'Climate Control Upgrade',
        'description': 'Enhanced climate system with additional zones and features',
        'estimated_amount': 1700.00,
    },
    {
        'category': 'Comfort',
        'name': 'Massage Seat Function',
        'description': 'Addition of massage functionality to driver and passenger seats',
        'estimated_amount': 2300.00,
    },
    {
        'category': 'Comfort',
        'name': 'Noise Reduction Package',
        'description': 'Additional sound insulation for quieter cabin',
        'estimated_amount': 1500.00,
    },
    {
        'category': 'Comfort',
        'name': 'Heated/Cooled Cup Holders',
        'description': 'Temperature-controlled cup holders for hot and cold beverages',
        'estimated_amount': 800.00,
    },
]
def reservation_details(request, id):
    """
    View the reservation checkout page.
    """
    booked_package = get_object_or_404(BookedPackage, reservation_number=id)
    
    remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

    initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
    midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
    balance_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))

    
    payments = PostPayment.objects.filter(rn_number=id)


    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    car_image = None
    if booked_package.car_model.images.exists():
        car_image = booked_package.car_model.images.first()
        
    
    # Check if there are pending features
    has_pending_features = booked_package.new_features.filter(status='pending').exists()
    
    # Calculate total pending amount if needed
    pending_features_total = booked_package.new_features.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'user_details': request.user,
        'booked_package': booked_package,
        'payments': payments,
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'car_image': car_image,
        'remaining_payment_after_reserve': remaining_payment_after_reserve,
        'initial_payment': initial_payment,
        'midway_payment': midway_payment,
        'balance_payment': balance_payment,
        'reservation_features': RESERVATION_FEATURE_OPTIONS,
        'has_pending_features': has_pending_features,
        'pending_features_total': pending_features_total,
    }

    return render(request, 'public/reservation_details.html', context)




@csrf_exempt
def initiate_build_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reservation_number = data.get('reservation_number')
            booked_package = get_object_or_404(BookedPackage, reservation_number=reservation_number)

            remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

            initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
            midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
            final_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))


            amount = Decimal('0')
            build_type = booked_package.build_type

            if build_type == 'initial_payment':
                amount = initial_payment
                previous_type = 'initial_payment'
            elif build_type == 'midway_payment':
                amount = midway_payment
                previous_type = 'midway_payment'
            elif build_type == 'final_payment':
                amount = final_payment
                previous_type = 'final_payment'

            print("Amount is", amount)

            customer = stripe.Customer.create(
                email=booked_package.user.email,
                name=f"{booked_package.user.first_name} {booked_package.user.last_name}",
                metadata={
                    'reservation_number': reservation_number,
                    'package_id': str(booked_package.id),
                    'user_id': str(booked_package.user.id),
                    'build_type': booked_package.build_type,
                    'build_status': booked_package.build_status
                }
            )

            # Create line item for Stripe checkout
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Build Payment - {booked_package.car_model.title}",
                        'description': f"Payment for {booked_package.build_type} stage of {booked_package.title} package",
                    },
                    'unit_amount': int(float(amount) * 100),  # amount in cents
                },
                'quantity': 1,
            }]

            # Prepare session data
            session_data = {
                'customer_id': customer.id,
                'line_items': line_items,
                'package_id': str(booked_package.id),
                'reservation_number': reservation_number,
                'success_url': request.build_absolute_uri(
                            f'/reservation/build-payment-success/{booked_package.id}/'
                            ) + '{CHECKOUT_SESSION_ID}'+'/',
                
                'cancel_url': request.build_absolute_uri(
                    f'/car/reservation-details/{booked_package.id}/'
                ),
                'metadata': {
                    'reservation_number': reservation_number,
                    'build_type': booked_package.build_type,
                    'build_status': booked_package.build_status,
                    'payment_type': 'build_payment'
                },
                'payment_intent_data': {
                    'description': f"Build payment for {booked_package.title} (Reservation: {reservation_number})",
                    'metadata': {
                        'reservation_number': reservation_number,
                        'build_type': booked_package.build_type,
                        'package_id': str(booked_package.id)
                    }
                }
            }

            return JsonResponse({
                'success': True,
                'session_data': session_data,
                'message': 'Payment session prepared successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@csrf_exempt
def create_build_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                customer=data['customer_id'],
                payment_method_types=['card'],
                line_items=data['line_items'],
                mode='payment',
                success_url=data['success_url'],
                cancel_url=data['cancel_url'],
                metadata=data['metadata'],
                payment_intent_data=data['payment_intent_data']
            )
            
            return JsonResponse({
                'success': True,
                'checkout_url': session.url,
                'session_id': session.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

def build_payment_success(request, id, sessionId):
    print("Session id is: ", sessionId)
    try:
        booked_package = get_object_or_404(BookedPackage, id=id)
        remaining_payment_after_reserve = booked_package.price - Decimal('100.00')

    # Calculate payments based on percentages from booked_package
        initial_payment = (remaining_payment_after_reserve * booked_package.initial_payment_percentage / Decimal('100')).quantize(Decimal('1'))
        midway_payment = (remaining_payment_after_reserve * booked_package.midway_payment_percentage / Decimal('100')).quantize(Decimal('1'))
        balance_payment = (remaining_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))

        amount = Decimal('0.00')
        previous_type = ''


        if booked_package.build_type == 'initial_payment':
            previous_type = booked_package.build_type
            amount = initial_payment
            booked_package.status = 'in_progress'
            booked_package.build_status = 'payment_done'
        elif booked_package.build_type == 'midway_payment':
            previous_type = booked_package.build_type
            amount = midway_payment
            booked_package.build_status = 'payment_done'
        elif booked_package.build_type == 'final_payment':
            previous_type = booked_package.build_type
            amount = balance_payment
            booked_package.build_status = 'payment_done'

        booked_package.remaining_price = booked_package.remaining_price - amount
        booked_package.save()

        current_site = get_current_site(request)
        print("Current site is : ",current_site)
        payment_date = timezone.now().strftime('%B %d, %Y')
        context = {
            'user': request.user,
            'booked_package': booked_package,
            'message': "Your " + ( "Initial Payment" if previous_type == 'initial_payment' else "Mid Way Payment " if previous_type == 'midway_payment' else "Final Balance Payment" if previous_type == 'final_payment' else "Order"  ) + " has been successfully processed.",
            'amount': str(amount),
            'payment_date': payment_date,
            'domain': current_site.domain,
            'reservation_number': booked_package.reservation_number,
        }

        # Render email template
        subject = 'Payment Confirmation - GEN-Z 40'
        html_content = render_to_string('email/payment_successful.html', context)
        plain_text = strip_tags(html_content)
        receipient_list = [booked_package.user.email, settings.ADMIN_EMAIL]
        sender = settings.EMAIL_FROM
        
        EmailThread(subject, html_content, receipient_list, sender).start()
        
        # send_mail(
        #     subject=subject,  
        #     message=plain_text,
        #     from_email=settings.EMAIL_FROM,
        #     recipient_list=[booked_package.user.email],  
        #     fail_silently=False,
        #     html_message=html_content
        # )

        if not sessionId:
            raise ValueError("No session ID provided")

        # Retrieve the Stripe session
        session = stripe.checkout.Session.retrieve(sessionId)
        print("Session Data is: ", session)
        
        # Create payment record
        booked_package_instance = BookedPackage.objects.get(reservation_number=booked_package.reservation_number)
        PostPayment.objects.create(
                user=booked_package.user,  
                rn_number=booked_package_instance,  
                stripe_payment_id=session.payment_intent,
                amount=float(amount),
                regarding=previous_type,
                currency="usd",
                status="succeeded",  
                package_name=booked_package.title,
        )
       
        

        return render(request, 'public/payment/success.html', {
            'is_footer_required': False,
            'message': 'Build payment completed successfully! A confirmation email has been sent.'
        })
    
    except Exception as e:
        # Log the error and show error page
        print(f"Error in build_payment_success: {str(e)}")
        return render(request, 'public/payment/success.html', {
            'is_footer_required': False,
            'message': 'Payment completed but there was an issue updating our records or sending the confirmation email. Please contact support.'
        })
    
def send_test_email(request,id):
    booked_package = get_object_or_404(BookedPackage, id=id)
    amount = 100
    current_site = get_current_site(request)
    try:
        context = {
                'user': request.user,
                'booked_package': booked_package,
                'amount': str(amount),  # Convert to string for template
                'payment_date': booked_package.updated_at,
                'domain': current_site.domain,
                'reservation_number': booked_package.reservation_number,
            }
        
        # Render the HTML template
        html_content = render_to_string('email/payment_successful.html', context)
        plain_text = strip_tags(html_content)  # Create a plain text version
        
        send_mail(
            subject="Test Email from Django",
            message=plain_text,  # Plain text version
            from_email=settings.EMAIL_FROM,
            recipient_list=["alijanali0091@gmail.com"],
            fail_silently=False,
            html_message=html_content  # HTML version
        )
        return HttpResponse("HTML Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}")
    


def add_reservation_feature(request, reservation_number):
    """
    Add a new feature to a booked package via AJAX.
    """
    booked_package = get_object_or_404(BookedPackage, reservation_number=reservation_number)
    
    if request.method == 'POST':
        feature_name = request.POST.get('feature')
        description = request.POST.get('description')
        amount = request.POST.get('amount')

        if not all([feature_name, description, amount]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required.'
            }, status=400)

        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid amount format.'
            }, status=400)

        # Create new feature with pending status
        ReservationNewFeatures.objects.create(
            booked_package=booked_package,
            features=feature_name,
            amount=amount,
            status='pending'
        )

        return JsonResponse({
            'success': True,
            'message': 'Feature added successfully. It is pending approval.',
            'reservation_number': reservation_number
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from decimal import Decimal
import json
import stripe
from backend.models import BookedPackage, ReservationNewFeatures, CustomUser

@csrf_exempt
def initiate_feature_payment(request, feature_id=None):
    """
    Initiate payment for a single feature or all pending features.
    Validates user ownership and feature status, creates a Stripe customer,
    and prepares data for the checkout session.
    :param feature_id: UUID of the feature to pay for (optional, None for 'pay all')
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    try:
        # Validate user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)

        # Parse JSON payload
        data = json.loads(request.body)
        reservation_number = data.get('reservation_number')
        if not reservation_number:
            return JsonResponse({
                'success': False,
                'message': 'Reservation number is required'
            }, status=400)

        # Get booked package and validate user ownership
        booked_package = get_object_or_404(
            BookedPackage,
            reservation_number=reservation_number,
            user=request.user
        )

        # Create Stripe customer
        customer = stripe.Customer.create(
            email=request.user.email,
            name=f"{request.user.first_name} {request.user.last_name}",
            metadata={
                'reservation_number': reservation_number,
                'user_id': str(request.user.id),
                'package_id': str(booked_package.id)
            }
        )

        if feature_id:
            # Handle single feature payment
            feature = get_object_or_404(
                ReservationNewFeatures,
                id=feature_id,
                booked_package=booked_package
            )

            if feature.status != 'pending':
                return JsonResponse({
                    'success': False,
                    'message': 'This feature is not available for payment'
                }, status=400)

            amount = Decimal(str(feature.amount))  # Convert float to Decimal
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Feature: {feature.features}",
                        'description': f"{feature.features} for {booked_package.car_model.title}",
                    },
                    'unit_amount': int(float(amount) * 100),  # Convert to cents
                },
                'quantity': 1,
            }]
            metadata = {
                'feature_id': str(feature.id),
                'reservation_number': reservation_number,
                'is_pay_all': 'false',
                'user_id': str(request.user.id)
            }

        else:
            # Handle "pay all" pending features
            pending_features = booked_package.new_features.filter(status='pending')
            if not pending_features.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'No pending features available for payment'
                }, status=400)

            amount = sum(Decimal(str(feature.amount)) for feature in pending_features)
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Multiple Features for {booked_package.car_model.title}",
                        'description': f"Payment for {pending_features.count()} features (Reservation: {reservation_number})",
                    },
                    'unit_amount': int(float(amount) * 100),  # Convert to cents
                },
                'quantity': 1,
            }]
            metadata = {
                'feature_ids': ','.join(str(feature.id) for feature in pending_features),
                'reservation_number': reservation_number,
                'is_pay_all': 'true',
                'user_id': str(request.user.id)
            }

        # Prepare session data
        session_data = {
            'customer_id': customer.id,
            'line_items': line_items,
            'package_id': str(booked_package.id),
            'reservation_number': reservation_number,
             'success_url': request.build_absolute_uri(
                            f'/feature/feature-payment-success/{reservation_number}/'
                            ) + '{CHECKOUT_SESSION_ID}'+'/',
            'cancel_url': request.build_absolute_uri(
                reverse('reservation_details', args=[reservation_number])
            ),
            'metadata': metadata,
            'payment_intent_data': {
                'description': f"Feature payment for {booked_package.car_model.title} (Reservation: {reservation_number})",
                'metadata': metadata
            }
        }

        return JsonResponse({
            'success': True,
            'session_data': session_data,
            'message': 'Payment session prepared successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON payload'
        }, status=400)
    except stripe.error.StripeError as e:
        return JsonResponse({
            'success': False,
            'message': f'Payment processing error: {str(e)}'
        }, status=400)
    except Exception as e:
        # Log error in production
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
def create_feature_checkout_session(request):
    """
    Create a Stripe checkout session for feature payment(s) using session data.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    try:
        # Parse JSON payload
        data = json.loads(request.body)

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            customer=data['customer_id'],
            payment_method_types=['card'],
            line_items=data['line_items'],
            mode='payment',
            success_url=data['success_url'],
            cancel_url=data['cancel_url'],
            metadata=data['metadata'],
            payment_intent_data=data['payment_intent_data']
        )

        return JsonResponse({
            'success': True,
            'checkout_url': session.url,
            'session_id': session.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON payload'
        }, status=400)
    except stripe.error.StripeError as e:
        return JsonResponse({
            'success': False,
            'message': f'Payment processing error: {str(e)}'
        }, status=400)
    except Exception as e:
        # Log error in production
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

def new_feature_payment_success(request, id, sessionId):
    """
    Handle successful feature payment and update feature status.
    Verifies the Stripe session and updates the corresponding feature(s).
    """
    session_id = sessionId
    reservation_number = id

    print("Session ID:", session_id, "Reservation Number:", reservation_number)
    if not all([session_id, reservation_number]):
        messages.error(request, "Invalid payment session or reservation number.")
        return redirect('reservation_details', reservation_number=reservation_number)

    try:
        # Retrieve Stripe session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Verify payment status
        if session.payment_status != 'paid':
            messages.error(request, "Payment not completed.")
            return redirect('reservation_details', reservation_number=reservation_number)

        # Verify reservation exists and user ownership
        booked_package = get_object_or_404(
            BookedPackage,
            reservation_number=reservation_number,
            user=request.user
        )

        is_pay_all = session.metadata.get('is_pay_all') == 'true'

        if is_pay_all:
            # Handle "pay all" features
            feature_ids = session.metadata.get('feature_ids', '').split(',')
            if not feature_ids or feature_ids == ['']:
                messages.error(request, "No features specified for payment.")
                return redirect('reservation_details', reservation_number=reservation_number)

            features = ReservationNewFeatures.objects.filter(
                id__in=feature_ids,
                booked_package=booked_package,
                status='pending'
            )
            if not features.exists():
                messages.error(request, "No valid pending features found.")
                return redirect('reservation_details', reservation_number=reservation_number)

            # Verify total amount
            expected_amount = sum(Decimal(str(feature.amount)) for feature in features)
            paid_amount = Decimal(str(session.amount_total / 100.0))
            if abs(expected_amount - paid_amount) > Decimal('0.01'):
                messages.error(request, "Payment amount mismatch.")
                return redirect('reservation_details', reservation_number=reservation_number)

            # Update features and create payment records
            for feature in features:
                feature.status = 'completed'
                feature.save()
                ReservationFeaturesPayment.objects.create(
                    reservation_feature=feature,
                    amount=Decimal(str(feature.amount)),
                    payment_status='completed',
                    payment_method='card',
                    transaction_id=session.payment_intent
                )
            messages.success(request, f"Payment successful! {features.count()} feature(s) added.")
        else:
            # Handle single feature payment
            feature_id = session.metadata.get('feature_id')
            if not feature_id:
                messages.error(request, "Feature ID not provided.")
                return redirect('reservation_details', id=reservation_number)

            feature = get_object_or_404(
                ReservationNewFeatures,
                id=feature_id,
                booked_package=booked_package,
                status='pending'
            )

            # Verify amount
            expected_amount = Decimal(str(feature.amount))
            paid_amount = Decimal(str(session.amount_total / 100.0))
            if abs(expected_amount - paid_amount) > Decimal('0.01'):
                messages.error(request, "Payment amount mismatch.")
                return redirect('reservation_details', id=reservation_number)

            # Update feature and create payment record
            feature.status = 'completed'
            feature.save()
            ReservationFeaturesPayment.objects.create(
                reservation_feature=feature,
                amount=expected_amount,
                payment_status='completed',
                payment_method='card',
                transaction_id=session.payment_intent
            )
            subject = "New Additional Feature Payment Confirmation- GEN-Z 40"
            current_site = get_current_site(request)
            context = {
                    'user': request.user,
                    'booked_package': booked_package,
                    'amount': 100,  # Convert to string for template
                    'payment_date': booked_package.updated_at,
                    'domain': current_site.domain,
                    'reservation_number': booked_package.reservation_number,
                }
            html_content = render_to_string('email/payment_successful.html', context)

            plain_text = strip_tags(html_content)
            receipient_list = [booked_package.user.email, settings.ADMIN_EMAIL]
            sender = settings.EMAIL_FROM
            
            EmailThread(subject, html_content, receipient_list, sender).start()
            messages.success(request, f"Payment successful! Feature '{feature.features}' added.")

        return redirect('reservation_details', id=reservation_number)

    except stripe.error.InvalidRequestError as e:
        messages.error(request, f"Invalid payment session: {str(e)}")
        return redirect('reservation_details', id=reservation_number)
    except stripe.error.StripeError as e:
        messages.error(request, f"Payment processing error: {str(e)}")
        return redirect('reservation_details', id=reservation_number)
    except Exception as e:
        # Log error in production
        messages.error(request, f"Error processing payment: {str(e)}")
        return redirect('reservation_details', id=reservation_number)
    



    # Dynamic Package Page
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from decimal import Decimal


def dynamic_configurator(request, car_model_slug):
    car_model = get_object_or_404(PostNavItem, slug=car_model_slug)
    
    packages = DynamicPackages.objects.all().order_by('created_at')
    
    sections = FeaturesSection.objects.all().order_by('created_at')
    
    rollerfeatures = PackageFeatureRoller.objects.all().order_by('created_at')
    rollerplusfeatures = PackageFeatureRollerPlus.objects.all().order_by('created_at')
    builderfeatures = PackageFeatureBuilder.objects.all().order_by('created_at')
    
    context = {
        'car_model': car_model,
        'packages': packages,
        'sections': sections,
        'rollerfeatures': rollerfeatures,
        'rollerplusfeatures': rollerplusfeatures,
        'builderfeatures': builderfeatures,
    }
    
    return render(request, 'public/DynamicConfigurator/configurator.html', context)
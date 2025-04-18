import json
import re
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from common.utils import EmailThread, get_client_ip
from django.templatetags.static import static
from .forms import PostContactForm, RegisterForm
from backend.models import CarConfiguration, BookedPackage , CustomUser, PostCommunity, PostCommunityJoiners, PostContactUs, PostNavItem, PostLandingPageImages, PostPackage, PostPayment, PostSubscribers
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from frontend.forms import PostSubscribeForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
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
    mail_subject = "Activate Your Account"
    print("User Details before sending activation email",current_site,user,random_password)
    html_message = render_to_string("email/activation_email.html", {
        "email": user.email,
        "password": random_password,
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    })
    
    # Create a plain text version for email clients that don't support HTML
    plain_message = strip_tags(html_message)
    print("Plain Message",plain_message)
    
    # Send mail with both HTML and plain text versions
    send_mail(
        subject=mail_subject,
        message=plain_message,  # Plain text version
        from_email=settings.EMAIL_FROM,
        recipient_list=[user.email],
        html_message=html_message  # HTML version
    )

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
                    EmailThread(subject, html_content, recipient_list, sender).start()
                    send_activation_email(request, user, request.POST['password1'])
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
    reserverd_vehicles = PostPayment.objects.filter(user_id=str(request.user.id), status='succeeded')
    context = {
        'reserverd_vehicles':reserverd_vehicles
    }
    return render(request, 'customer/reserved_vehicles/payments.html', context, {'is_footer_required': True})

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
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            zip_code = request.POST.get('zip_code')
            amount = request.POST.get('amount')
            package_id = request.POST.get('package_id')

            # Get the booked package
            booked_package = BookedPackage.objects.get(id=package_id)
            
            # Create a Stripe customer
            customer = stripe.Customer.create(
                email=email,
                name=f"{first_name} {last_name}",
                phone=phone_number,
                metadata={
                    'package_id': str(package_id),
                    'user_email': email,
                    'zip_code': zip_code
                }
            )

            # Create line items for Stripe checkout
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

            # Prepare session data to be used in create_checkout_session
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
        # Get the booked package
        
        booked_package = BookedPackage.objects.get(id=id)
        booked_package.status = 'confirmed'
        booked_package.save()
        
        
        # Get the session ID from the query parameters (Stripe redirects with session_id)
        # session_id = request.GET.get('session_id')
        if sessionId:
            # Retrieve the Stripe session to get payment details
            session = stripe.checkout.Session.retrieve(sessionId)

            print("Session Response is : ",session);
            
            # Create payment record
            PostPayment.objects.create(
                user=booked_package.user,  # Assuming BookedPackage has a user field
                rn_number=booked_package.reservation_number,
                stripe_payment_id=session.payment_intent,
                amount=100,  # Assuming price is stored in booked_package
                regarding="reserve",
                currency="usd",
                status="succeeded",  # Or you can check session.payment_status
                package_name=booked_package.title,
            )
            
        
            # time.sleep(5)


        return render(request, 'public/payment/success.html', {'is_footer_required': False})
    
    except Exception as e:
        # Handle errors appropriately - maybe log them and still show success page
        print(f"Error in reservation_success: {str(e)}")
        return render(request, 'public/payment/success.html', {'is_footer_required': False})



def reservation_details(request, id):
    """
    View the reservation checkout page.
    """
    booked_package = get_object_or_404(BookedPackage, reservation_number=id)
    
    # Ensure you're using Decimal for all calculations
    remaing_payment_after_reserve = booked_package.price - Decimal('100.00')
    initial_payment = (remaing_payment_after_reserve * Decimal('0.40')).quantize(Decimal('1'))
    midway_payment = (remaing_payment_after_reserve * Decimal('0.40')).quantize(Decimal('1'))
    balance_payment = (remaing_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))
    
    payments = PostPayment.objects.filter(rn_number=id)

    # Get user location data
    ip = get_country_info(request)
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country')
    country_flag_url = f'https://www.flagsapi.com/{country_code}/flat/64.png'

    car_image = None
    if booked_package.car_model.images.exists():
        car_image = booked_package.car_model.images.first()

    context = {
        'user_details': request.user,
        'booked_package': booked_package,
        'payments': payments,
        'country_code': country_code,
        'country_flag_url': country_flag_url,
        'car_image': car_image,
        'remaining_payment_after_reserve': remaing_payment_after_reserve,
        'initial_payment': initial_payment,
        'midway_payment': midway_payment,
        'balance_payment': balance_payment,
    }

    return render(request, 'public/reservation_details.html', context)




@csrf_exempt
def initiate_build_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reservation_number = data.get('reservation_number')
            booked_package = get_object_or_404(BookedPackage, reservation_number=reservation_number)
            remaing_payment_after_reserve = booked_package.price - Decimal('100.00')
            initial_payment = (remaing_payment_after_reserve * Decimal('0.40')).quantize(Decimal('1'))
            midway_payment = (remaing_payment_after_reserve * Decimal('0.40')).quantize(Decimal('1'))
            balance_payment = (remaing_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))
            amount = Decimal('0')
            previous_type = ''
            if booked_package.build_type == 'order_confirmed':
                amount = initial_payment
                previous_type = 'order_confirmed'
            elif booked_package.build_type == 'body_complete':
                amount = midway_payment
                previous_type = 'body_complete'
            elif booked_package.build_type == 'built':
                amount = balance_payment
                previous_type = 'built'

            print("Amount is ",amount)
            
            

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


def build_payment_success(request, id,sessionId):
    print("Seesion id is : ",sessionId)
    try:
        booked_package = get_object_or_404(BookedPackage, id=id)
        remaing_payment_after_reserve = booked_package.price - Decimal('100.00')
        initial_payment = (remaing_payment_after_reserve * Decimal('0.40')).quantize(Decimal('1'))
        midway_payment = (remaing_payment_after_reserve * Decimal('0.40')).quantize(Decimal('1'))
        balance_payment = (remaing_payment_after_reserve - (initial_payment + midway_payment)).quantize(Decimal('1'))
        amount = Decimal('0')
        previous_type = ''
        if booked_package.build_type == 'order_confirmed':
            previous_type = booked_package.build_type
            amount = initial_payment
            booked_package.status = 'in_progress'
            booked_package.build_status = 'completed'
            booked_package.save()

        elif booked_package.build_type == 'body_complete':
            previous_type = booked_package.build_type
            amount = midway_payment
            booked_package.build_type = 'assembly'
            booked_package.build_status = 'in_progress'
            booked_package.save()
        elif booked_package.build_type == 'built':
            previous_type = booked_package.build_type
            amount = balance_payment
            booked_package.build_type = 'quality_check'
            booked_package.build_status = 'in_progress'
            booked_package.save()

        
       
        if sessionId:
            # Retrieve the Stripe session
            session = stripe.checkout.Session.retrieve(sessionId)
            print("Sesstion Data is : ",session)
            
            # Create payment record
            PostPayment.objects.create(
                user=booked_package.user,
                rn_number=booked_package.reservation_number,
                stripe_payment_id=session.payment_intent,
                amount=float(amount),
                regarding=previous_type,
                currency="usd",
                status="succeeded",
                package_name=booked_package.title,
                )
        
            return render(request, 'public/payment/success.html', {
                'is_footer_required': False,
                'message': 'Build payment completed successfully!'
            })
    
    except Exception as e:
        # Log the error and still show success page
        print(f"Error in build_payment_success: {str(e)}")
        return render(request, 'public/payment/success.html', {
            'is_footer_required': False,
            'message': 'Payment completed but there was an issue updating our records. Please contact support.'
        })
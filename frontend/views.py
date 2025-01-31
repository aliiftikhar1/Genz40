import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from common.utils import get_client_ip
from .forms import PostContactForm, RegisterForm
from backend.models import CustomUser, PostCommunity, PostCommunityJoiners, PostNavItem, PostLandingPageImages, PostPackage, PostPayment, PostSubscribers
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from frontend.forms import PostSubscribeForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
import string
import random
from django.contrib.auth import login
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import HttpResponse
import datetime
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_country_info(request):
    ip = get_client_ip(request)

    # response = requests.get(f'http://api.ipstack.com/{ip}?access_key={settings.IPSTACK_API_KEY}')
    # data = response.json()
    # country_code = data.get('country_code')
    return ip

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)
    random_password = generate_random_password()
    # ip = get_country_info(request)
    ip = "103.135.189.223"
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

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def register_page(request):
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
        'random_password': random_password
    }
    return render(request, 'registration/register.html', context)


def get_register_community(request):
    if request.method == 'POST':
        if not CustomUser.objects.filter(email=request.POST['email']).exists():
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                random_password = generate_random_password()
                user.set_password(random_password)
                user.save()
                PostCommunityJoiners.objects.create(user=user)
                # login(request, user)
                return JsonResponse({"message": "Thank You for Joining. This Feature is currently under progress and you will be automatically added in our community once it's developed.", 'is_success': True})       
        else:
                user = CustomUser.objects.get(email=request.POST['email'])
                if not PostCommunityJoiners.objects.filter(user=user.id).exists():
                    PostCommunityJoiners.objects.create(user=user)
                    return JsonResponse({"message": 'Successfully added.', 'is_success': True})
                else:
                    return JsonResponse({"message": 'Already joined.', 'is_success': False})
        return JsonResponse({"message": 'Already joined.', 'is_success': False})

def get_register(request):
    if request.method == 'POST':
        if not CustomUser.objects.filter(email=request.POST['email']).exists():
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                random_password = generate_random_password()
                user.set_password(random_password)
                user.save()
                return JsonResponse({"message": 'Successfully added. Please check mailbox for password.', 'is_success': True})       
        else:
            return JsonResponse({"message": 'Already joined.', 'is_success': False})
      
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print('-------user', user.id)
            return JsonResponse({"message": 'Login successfully.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Invalid username or password.', 'is_success': False})
    else:
        return render(request, 'registration/login.html')


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
    
def subscribe(request):
    if request.method == 'POST':
        if not PostSubscribers.objects.filter(email=request.POST['email']).exists():
            form = PostSubscribeForm(request.POST)
            if form.is_valid():
                form.save()
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

def car_details(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package_details = PostPackage.objects.filter(is_active=True, nav_item=items.id).order_by('position')
    amount_due = package_details[0].amount_due
    # package = items.details.filter(is_active=True).order_by('position')
    print('---------package', package_details[0].amount_due)
    random_password = generate_random_password()
    # ip = get_country_info(request)
    ip = "103.135.189.223"
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

def save_contact(request):
    if request.method == 'POST':
        form = PostContactForm(request.POST)
        print('--------form', form)
        if form.is_valid():
            form.save()
            subject = 'Thank you for Newsletter subscribe - www.genz40.com'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [settings.ADMIN_EMAIL]
            c = {'name': 'Salman'}
            html_content = render_to_string('email/contact_admin.html', c)
            send_mail(subject, html_content, email_from, recipient_list, fail_silently=False,
                        html_message=html_content)
            return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Something went wrong. Please try again!', 'is_success': False})

def generate_reference_number():
    # Get today's date in MMDDYY format
    today_date = datetime.datetime.today().strftime('%m%d%y')

    # Get the last inserted number from the database
    last_entry = PostPayment.objects.order_by('-created_at').first()  # Get last record
    last_number = int(last_entry.rn_number[-4:]) if last_entry else 1004  # Start from 1000 if no entry exists
    print('-------last_number', last_number)
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
        if not CustomUser.objects.filter(email=request.POST['email'], phone_number=request.POST['phone_number']).exists():
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                random_password = generate_random_password()
                user.set_password(random_password)
                user.zip_code = request.POST['zip_code']
                user.save()
                # user = form.get_user()
                login(request, user)
                if(user.id):
                    fullName = user.first_name+ ' '+user.last_name
                    return create_checkout_session(product_name, amount, user.email, fullName, user.id, new_ref)     
        else:
            fullName = request.user.first_name+ ' '+request.user.last_name
            return create_checkout_session(product_name, amount, request.user.email, fullName, request.user.id, new_ref)
             
def create_checkout_session(product_name, amount, email, full_name, user_id, new_ref):
    currency = "usd"
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': product_name,
                    'description': 'This reservation will save your position in line. When you car is available for production, we will invite you to configure and choose from dozens of options to make it complete personalized and unique.',
                    'images': ['https://genz40.com/static/images/genz/mark1-builder4.png'],
                },
                'unit_amount': int(amount)*100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://genz40.com/success/',
        cancel_url='https://genz40.com/cancel/',
        # success_url='http://127.0.0.1:8000/success/',
        # cancel_url='http://127.0.0.1:8000/cancel/',
        customer_email=email,  # Pass email to prefill the Stripe Checkout form
        metadata={
            'full_name': full_name,  # Pass full name as metadata
            'email': email
        },
        payment_intent_data={
        'description': str(user_id), #Passing Userid
        "metadata": {
            'new_ref':new_ref,
            'product_name': product_name
        },
        },
        # custom_fields=[{
        #     "key": "custom_note",
        #     "label": {"type": "custom", "custom": new_ref},
        #     "type": "text"
        # }],
    )

    return redirect(session.url, code=303)

    # return render(request, 'public/payment/checkout.html')

def payment_success(request):
    return render(request, 'public/payment/success.html', {'is_footer_required': False})

def payment_cancel(request):
    return render(request, 'public/payment/cancel.html', {'is_footer_required': False})

STRIPE_WEBHOOK_SECRET= 'whsec_559bd2071b3e1bf765d4ad825586dcaab38522c998fcccd802bc40f1d90f84c9'

@csrf_exempt  # Webhooks don't require CSRF protection
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
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
        # print('------payment_intent', payment_intent)
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
    elif event['type'] == 'payment_intent.succeeded':
        print('=======================')
    else:
        print(f"Unhandled event type: {event['type']}")

    return JsonResponse({'success': True})

@login_required
def my_vehicles(request):
    reserverd_vehicles = PostPayment.objects.filter(user_id=str(request.user.id), status='succeeded')
    context = {
        'reserverd_vehicles':reserverd_vehicles
    }
    return render(request, 'customer/reserved_vehicles/my_vehicles.html', context, {'is_footer_required': True})

@login_required
def my_vehicle_details(request, id):
    reserverd_vehicle = PostPayment.objects.get(id=id)
    context = {
        'reserverd_vehicle':reserverd_vehicle
    }
    return render(request, 'customer/reserved_vehicles/vehicle_details.html', context, {'is_footer_required': True})

@login_required
def payment_history(request):
    return render(request, 'customer/reserved_vehicles/payments.html', {'is_footer_required': True})

@login_required
def profile_settings(request):
    return render(request, 'customer/profile/profile_settings.html', {'is_footer_required': True})

@login_required
def customer_message(request):
    return render(request, 'customer/message/message.html', {'is_footer_required': True})
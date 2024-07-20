import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from common.utils import get_client_ip
from .forms import PostContactForm, RegisterForm
from backend.models import CustomUser, PostCommunity, PostCommunityJoiners, PostNavItem, PostLandingPageImages, PostSubscribers
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from frontend.forms import PostSubscribeForm
from django.conf import settings
import string
import random
from django.contrib.auth import login
from django.http import JsonResponse
import requests


def get_country_info(request):
    ip = get_client_ip(request)

    # response = requests.get(f'http://api.ipstack.com/{ip}?access_key={settings.IPSTACK_API_KEY}')
    # data = response.json()
    # country_code = data.get('country_code')
    return ip

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)
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
        'section_1': section_1,
        'section_2': section_2,
        'section_3': section_3,
        'navbar_style': 'dark',
        # 'form': form,
        'random_password': random_password
    }

    return render(request, 'public/index.html', context)

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def get_register(request):
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
                return JsonResponse({"message": 'Successfully added. Please check mailbox for password.', 'is_success': True})       
        else:
                user = CustomUser.objects.get(email=request.POST['email'])
                if not PostCommunityJoiners.objects.filter(user=user.id).exists():
                    PostCommunityJoiners.objects.create(user=user)
                    return JsonResponse({"message": 'Successfully added.', 'is_success': True})
                else:
                    return JsonResponse({"message": 'Already joined.', 'is_success': False})
        return JsonResponse({"message": 'Already joined.', 'is_success': False})
    
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({"message": 'Login successfully.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Invalid username or password.', 'is_success': False})

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


def about(request):
    return render(request, 'public/about.html', {
        'navbar_style': 'dark'
    })


def blog(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/blog.html')

def contact_us(request):
    return render(request, 'public/contact_us.html')


def terms_conditions(request):
    return render(request, 'public/terms_conditions.html')

def privacy_policy(request):
    return render(request, 'public/privacy_policy.html')

def save_contact(request):
    if request.method == 'POST':
        form = PostContactForm(request.POST)
        if form.is_valid():
            form.save()
            subject = 'Mail from GENZ - Contact Us'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [settings.ADMIN_EMAIL]
            c = {'name': 'Salman'}
            html_content = render_to_string('email/subscribe_user.html', c)
            send_mail(subject, html_content, email_from, recipient_list, fail_silently=False,
                        html_message=html_content)
            return JsonResponse({"message": 'Thank you for contacting us. GENZ team will reach you shortly.', 'is_success': True})
        else:
            return JsonResponse({"message": 'Something went wrong. Please try again!', 'is_success': False})
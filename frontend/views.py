import json
from django.shortcuts import render, redirect, get_object_or_404
from backend.models import PostNavItem, PostLandingPageImages


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    section_3 = get_object_or_404(PostLandingPageImages, section=3)
    return render(request, 'public/index.html', {'section_1': section_1,
                                                 'section_2': section_2,
                                                 'section_3': section_3,
                                                 'navbar_style': 'dark'})


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

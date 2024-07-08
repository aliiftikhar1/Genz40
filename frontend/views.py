from django.shortcuts import render, redirect, get_object_or_404
from backend.models import PostNavItem


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    return render(request, 'public/index.html')


def navitem_detail(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    package = items.details.filter(is_active=True).order_by('position')
    return render(request, 'public/navitem_detail.html',
                  {'items': items,
                   'packages': package})


def about(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/about.html',
                  {'items': items})


def blog(request, slug):
    items = get_object_or_404(PostNavItem, slug=slug)
    return render(request, 'public/blog.html')

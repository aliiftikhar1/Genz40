import json
from django.shortcuts import render, redirect, get_object_or_404
from backend.models import PostNavItem, PostLandingPageImages


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    section_1 = get_object_or_404(PostLandingPageImages, section=1)
    # filtered_tags = PostLandingPageImages.objects.filter(section=1)
    section_2 = get_object_or_404(PostLandingPageImages, section=2)
    # # data_names = PostLandingPageImages.objects.values_list('title_data', flat=True)
    # # data_names = list(filtered_tags.values_list('title_data', flat=True))
    # # data_names_list = list(filtered_tags.title_data)
    # tag_names = list(PostLandingPageImages.objects.filter(section=1).values_list('title_data', flat=True))
    # initial_string = section_1.title_data
    # print('--------tags', type(initial_string))
    # # Convert the string to a list
    # initial_list = initial_string.split(', ')
    # print('--------initial_list', initial_list)
    # tag_list = str(section_1.title_data).split(', ')
    # print('-------tag_list', tag_list)

    # json_string = json.dumps(initial_list)
    # converted_list = json.loads(json_string)

    # print('-------converted_list', converted_list)
    # # tag_names_string = ", ".join(PostLandingPageImages.objects.filter(section=1).values_list('title_data', flat=True))
    return render(request, 'public/index.html', { 'section_1': section_1, 'section_2': section_2 })


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

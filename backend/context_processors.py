# myapp/context_processors.py
from .models import PostNavItem


def nav_items(request):
    # Get only active parent items
    nav_items = PostNavItem.objects.filter(parent__isnull=True, is_active=True).order_by('position')
    for item in nav_items:
        # Assign active children to a new attribute
        item.active_children = item.get_active_children()
    return {'nav_items': nav_items}


# def nav_items(request):
#     return {
#         'nav_items': PostNavItem.objects.filter(parent__isnull=True, is_active=True).order_by('position')
#     }

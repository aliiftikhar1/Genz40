# myapp/context_processors.py
from .models import PostNavItem
from django.conf import settings
from django.contrib.auth.models import AnonymousUser



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

def add_user_to_context(request):
    user_data = {}

    if request.user and isinstance(request.user, AnonymousUser):
        user_data['is_authenticated'] = False
        user_data['user_id'] = None
    else:
        user_data['is_authenticated'] = True
        user_data['user_id'] = str(request.user.id)  # Ensure you convert the UUID to a string if necessary
        user_data['email'] = request.user.email
        user_data['full_name'] = request.user.first_name + ' '+ request.user.last_name
        user_data['is_delete'] = request.user.is_delete
        user_data['is_email_verified'] = request.user.is_email_verified
        user_data['base_url'] = settings.BASE_URL
        user_data['role'] = request.user.role
    return {'user_data': user_data}
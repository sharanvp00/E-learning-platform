from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from functools import wraps

def login_required_with_popup(view_func):
    """
    Custom decorator that shows a popup when a user tries to access a page that requires login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to login page with a parameter to show the popup
            login_url = reverse('login') + '?login_required=true'
            return redirect(login_url)
    return wrapper
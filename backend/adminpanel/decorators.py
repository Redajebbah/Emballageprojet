from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps


def admin_required(view_func):
    """Decorator to require login and membership in 'admin' group."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Redirect to adminpanel login if not authenticated or not in admin group
        if not request.user.is_authenticated:
            return redirect(f"{reverse('adminpanel:login')}?next={request.path}")

        user = request.user
        if not (user.groups.filter(name='admin').exists() or user.is_superuser):
            return redirect(f"{reverse('adminpanel:login')}?next={request.path}")

        return view_func(request, *args, **kwargs)

    return _wrapped

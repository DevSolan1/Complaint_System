"""Role-based access control decorators for function-based views."""
from functools import wraps
from typing import Callable, Iterable

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles: str) -> Callable:
    """Restrict a view to users whose ``role`` is in ``roles`` (superusers always allowed)."""

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this page.")

        return _wrapped

    return decorator


def manager_required(view_func: Callable) -> Callable:
    return role_required("manager")(view_func)


def staff_required(view_func: Callable) -> Callable:
    """Agents or managers."""
    return role_required("agent", "manager")(view_func)

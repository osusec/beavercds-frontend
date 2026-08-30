from functools import wraps

from django.core.exceptions import PermissionDenied


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


def admin_required():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_admin:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator

from django.shortcuts import render
from django.http import JsonResponse
from functools import wraps
from bctf.settings import CTF_EVENT_START_PARSED, CTF_EVENT_END_PARSED
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
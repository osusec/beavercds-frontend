from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from functools import wraps
from bctf.settings import CTFTIME_OAUTH_CLIENTID


class CTFTimeOAuthMixin:
    def dispatch(self, request, *args, **kwargs):
        if not CTFTIME_OAUTH_CLIENTID:
            return redirect(reverse_lazy('login'))
        return super().dispatch(request, *args, **kwargs)

def ctftime_oauth():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not CTFTIME_OAUTH_CLIENTID:
                return redirect(reverse_lazy('login'))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

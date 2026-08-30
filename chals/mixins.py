from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from bctf.settings import CTF_EVENT_END, CTF_EVENT_START


class CTFStartMixin:
    def dispatch(self, request, *args, **kwargs):
        if timezone.now() < CTF_EVENT_START:
            return render(request, "not_started.html", status=403)
        return super().dispatch(request, *args, **kwargs)


def ctf_start():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if timezone.now() < CTF_EVENT_START:
                return render(request, "not_started.html", status=403)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


class CTFEndMixin:
    def dispatch(self, request, *args, **kwargs):
        if timezone.now() > CTF_EVENT_END:
            return JsonResponse({"errors": ["The CTF has ended."]}, status=403)
        return super().dispatch(request, *args, **kwargs)


def ctf_end():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if timezone.now() > CTF_EVENT_END:
                return JsonResponse({"errors": ["Flag was incorrect."]}, status=403)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

from django.contrib import admin
from django.urls import path, include
from .views import *
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    # API endpoints below
    path ('api/checkaccess', CheckAccess.as_view(), name='check-access'),
    path ('api/resolvestate', ResolveState.as_view(), name='resolve-state'),
]

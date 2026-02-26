##

from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path ('', login_required(ListChal), name='chals-list'),
    # API endpoints below
    path ('checkaccess/', CheckAccess, name='check-access'),
    path ('resolvestate/', ResolveState, name='resolve-state'),
]

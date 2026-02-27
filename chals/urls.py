from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path ('', login_required(ListChal), name='chals-list'),
]

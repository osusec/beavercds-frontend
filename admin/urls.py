#
# Admin urls.py
#

from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path ('', AdminHome.as_view(), name='admin-home'),
    path ('chals/', AdminChals.as_view(), name='admin-chals'),
    path ('solves/', AdminSolves.as_view(), name='admin-solves'),
    path ('teams/', AdminTeams.as_view(), name='admin-teams'),
]

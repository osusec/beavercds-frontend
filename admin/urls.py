#
# Admin urls.py
#

from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    path ('chals/', AdminChals.as_view(), name='admin-chals'),
    path ('solves/', AdminSolves.as_view(), name='admin-solves'),
    path ('teams/', AdminTeams.as_view(), name='admin-teams'),
    path ('teams/changebracket/', ChangeBracketAdm.as_view(), name='change_bracket_adm'),
    path ('teams/deactivate/', DeactivateTeam.as_view(), name='deactivate-team'),
    path ('teams/activate/', ActivateTeam.as_view(), name='activate-team'),
]

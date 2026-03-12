from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .models import CTFTime_Team, CTFTeam_ContactEmails, CTFTeam
from .forms import TeamCreationForm
from django.contrib.auth import login, authenticate

from bctf.settings import OAUTH, LOGIN_REDIRECT_URL


class SignUpView(generic.CreateView):
    form_class = TeamCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def ProfilePage (request):
    pass


def oauth_step1(request):
    redirect_uri = request.build_absolute_uri(reverse_lazy('oauth-step2'))
    return OAUTH.ctftime.authorize_redirect(request, redirect_uri)

def oauth_step2(request):
    authed_team = authenticate(request)
    
    if not authed_team:
        return redirect(reverse_lazy('login'))

    login(request, authed_team)
    print(f'Logged in team {authed_team.team_name}')
    return redirect(LOGIN_REDIRECT_URL)

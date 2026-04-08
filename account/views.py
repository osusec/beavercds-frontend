from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic, View
from .models import CTFTime_Team, CTFTeam_ContactEmails, CTFTeam, CTFTeam_LongtermTokens
from .forms import TeamCreationForm
from django.contrib.auth import login, authenticate
import secrets
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin

from bctf.settings import OAUTH, LOGIN_REDIRECT_URL, TOKEN_LENGTH


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
    print(f'Logged in team {authed_team.team_name} by CTFTime')
    return redirect(LOGIN_REDIRECT_URL)


class TokenAuth (View):
    # Authenticate with the token
    def get (self, request):
        token = request.GET['token']
        if not token:
            return redirect(reverse_lazy('login'))

        authed_team = authenticate (request, token=token)
        if not authed_team:
            return redirect(reverse_lazy('login'))
        
        login (request, authed_team)
        print(f'Logged in team {authed_team.team_name} by token')
        return authed_team


class CreateToken (View, LoginRequiredMixin):
    def post (self, request):
        team = request.user

        # Only have one token at a time
        if CTFTeam_LongtermTokens.objects.filter(team=team).exists():
            # TODO: return errors
            return redirect(reverse_lazy('profile-home'))

        saved = False
        while not saved:
            try:
                new_token = secrets.token_urlsafe(TOKEN_LENGTH)
                team_token_obj = CTFTeam_LongtermTokens(
                    team=team,
                    token=new_token
                )
                team_token_obj.save()
                saved = True
            except IntegrityError:
                saved = False

        return redirect(reverse_lazy('profile-home'))


class DeleteToken (View, LoginRequiredMixin):
    def post (self, request):
        team = request.user
        CTFTeam_LongtermTokens.objects.filter(team=team).delete()

        return redirect(reverse_lazy('profile-home'))
        
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic, View
from .models import *
from chals.models import ChallengeSolve, Challenge
from .forms import *
from django.contrib.auth import login, authenticate
import secrets
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin

from bctf.settings import OAUTH, LOGIN_REDIRECT_URL, TOKEN_LENGTH


class SignUpView(generic.CreateView):
    form_class = TeamCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProfilePage (LoginRequiredMixin, View):
    def get (self, request):
        team = request.user

        ctftime_bool = CTFTime_Team.objects.filter(team=team).exists()

        access_tokens = (
            CTFTeam_LongtermTokens.objects
            .filter(team=team)
        )

        contact_emails = (
            CTFTeam_ContactEmails.objects
            .filter(team=team)
        )

        solves = (
            ChallengeSolve.objects
            .filter(team=team, challenge__active=True)
            .order_by('-time_of_solve')
        )

        return render (request, "registration/profile.html", {'ctftime_team': ctftime_bool, 'access_tokens': access_tokens, 'contact_emails': contact_emails, 'solves': solves, 'addcontact_form': AddContactEmailForm})


class OAuth_Step1 (View):
    def get (self, request):
        redirect_uri = request.build_absolute_uri(reverse_lazy('oauth-step2'))
        return OAUTH.ctftime.authorize_redirect(request, redirect_uri)


class OAuth_Step2 (View):
    def get (self, request):
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


class CreateToken (LoginRequiredMixin, View):
    def post (self, request):
        team = request.user

        # TODO why not
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


class DeleteToken (LoginRequiredMixin, View):
    def post (self, request):
        team = request.user

        # check that authz worked correctly here
        form = TokenDeleteForm(request.user, request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            token.delete()

        return redirect(reverse_lazy('profile-home'))

class AddContactEmail (LoginRequiredMixin, View):
    def post (self, request):
        team = request.user

        form = AddContactEmailForm(request.POST)
        if form.is_valid():
            email_addr = form.cleaned_data['email']
            new_email = CTFTeam_ContactEmails(team=team, email=email_addr)
            new_email.save()

        return redirect(reverse_lazy('profile-home'))

class DeleteContactEmail (LoginRequiredMixin, View):
    def post (self, request):
        team = request.user

        # TODO: check that authz worked correctly here
        form = RemoveContactEmailForm(request.user, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            email.delete()
        
        return redirect(reverse_lazy('profile-home'))
        
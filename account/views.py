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
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    JsonResponse,
)

from bctf.settings import OAUTH, LOGIN_REDIRECT_URL, TOKEN_LENGTH


class SignUpView(generic.CreateView):
    form_class = TeamCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class ProfilePage(LoginRequiredMixin, View):
    def get(self, request):
        team = request.user

        ctftime_bool = CTFTime_Team.objects.filter(team=team).exists()

        access_tokens = CTFTeam_LongtermTokens.objects.filter(team=team)

        contact_emails = CTFTeam_ContactEmails.objects.filter(team=team)

        solves = ChallengeSolve.objects.filter(
            team=team, challenge__active=True
        ).order_by("-time_of_solve")

        return render(
            request,
            "registration/profile.html",
            {
                "ctftime_team": ctftime_bool,
                "access_tokens": access_tokens,
                "contact_emails": contact_emails,
                "solves": solves,
                "addcontact_form": AddContactEmailForm,
            },
        )


class OAuth_Step1(View):
    def get(self, request):
        redirect_uri = request.build_absolute_uri(reverse_lazy("oauth-step2"))
        return OAUTH.ctftime.authorize_redirect(request, redirect_uri)


class OAuth_Step2(View):
    def get(self, request):
        authed_team = authenticate(request)

        if not authed_team:
            return redirect(reverse_lazy("login"))

        login(request, authed_team)
        return redirect(LOGIN_REDIRECT_URL)


class TokenAuth(View):
    # Authenticate with the token
    def get(self, request):
        token = request.GET["token"]
        if not token:
            return redirect(reverse_lazy("login"))

        authed_team = authenticate(request, token=token)
        if not authed_team:
            return redirect(reverse_lazy("login"))

        login(request, authed_team)
        return redirect(LOGIN_REDIRECT_URL)


class CreateToken(LoginRequiredMixin, View):
    def post(self, request):
        team = request.user

        # Don't have too many active tokens at a time
        if CTFTeam_LongtermTokens.objects.filter(team=team).count() >= 4:
            return JsonResponse(
                {"errors": ["Only 4 access links can be active at once."]}, status=400
            )

        saved = False
        while not saved:
            try:
                new_token = secrets.token_urlsafe(TOKEN_LENGTH)
                team_token_obj = CTFTeam_LongtermTokens(team=team, token=new_token)
                team_token_obj.save()
                saved = True
            except IntegrityError:
                saved = False

        return JsonResponse({"redirect": reverse_lazy("profile-home")})


class DeleteToken(LoginRequiredMixin, View):
    def post(self, request):
        team = request.user

        form = TokenDeleteForm(request.user, request.POST)
        if form.is_valid():
            token = form.cleaned_data["token"]
            token.delete()
            return JsonResponse({"redirect": reverse_lazy("profile-home")})
        else:
            return JsonResponse({"errors": ["Link not found."]}, status=404)


class AddContactEmail(LoginRequiredMixin, View):
    def post(self, request):
        team = request.user

        form = AddContactEmailForm(request.POST)
        if form.is_valid():
            email_addr = form.cleaned_data["email"]
            new_email = CTFTeam_ContactEmails(team=team, email=email_addr)
            new_email.save()
            return JsonResponse({"redirect": reverse_lazy("profile-home")})
        else:
            errors = []
            for field, err in form.errors.items():
                for inst in err:
                    errors.append(inst)
            return JsonResponse({"errors": errors}, status=400)


class DeleteContactEmail(LoginRequiredMixin, View):
    def post(self, request):
        team = request.user

        form = RemoveContactEmailForm(request.user, request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            email.delete()
            return JsonResponse({"redirect": reverse_lazy("profile-home")})
        else:
            return JsonResponse({"errors": ["Email not found."]}, status=404)

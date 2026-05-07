import requests
from django.contrib.auth.backends import BaseBackend
from django.http import HttpResponseServerError

from bctf.settings import OAUTH

from .models import CTFTeam, CTFTeam_ContactEmails, CTFTeam_LongtermTokens, CTFTime_Team


class CTFTime_OAuth_Backend(BaseBackend):
    def authenticate(self, request):
        try:
            # Any error here will be a 500 Internal Server Error
            # Can trigger this either by tampering or replaying
            #  state or tampering the access code
            token = OAUTH.ctftime.authorize_access_token(request)
        except:
            return None

        access_token = token["access_token"]
        token_type = token["token_type"].capitalize()

        oauth_api_resp = requests.get(
            OAUTH.ctftime.api_base_url,
            headers={"Authorization": f"{token_type} {access_token}"},
        )
        if oauth_api_resp.status_code != 200:
            print(
                f"CTFTime OAuth: call to API endpoint {OAUTH.ctftime.api_base_url} returned {oauth_api_resp.status_code} {oauth_api_resp.reason}"
            )
            return None

        oauth_user_information = oauth_api_resp.json()
        try:
            # Login existing team
            existing_ctftime = CTFTime_Team.objects.get(
                pk=oauth_user_information["team"]["id"]
            )
            existing_team = existing_ctftime.team

            team_emails = CTFTeam_ContactEmails.objects.filter(
                team=existing_team, email=oauth_user_information["email"]
            )
            if team_emails.count() == 0:
                new_team_email = CTFTeam_ContactEmails(
                    team=existing_team, email=oauth_user_information["email"]
                )
                new_team_email.save()

            return existing_team

        except CTFTime_Team.DoesNotExist:
            # Register new team
            new_team = CTFTeam(
                team_name=oauth_user_information["team"]["name"], ctftime_bool=True
            )
            new_team.set_unusable_password()
            new_ctftime = CTFTime_Team(
                ctftime_id=oauth_user_information["team"]["id"], team=new_team
            )
            new_team_email = CTFTeam_ContactEmails(
                team=new_team, email=oauth_user_information["email"]
            )
            new_team.save()
            new_ctftime.save()
            new_team_email.save()

            return new_team

    def get_user(self, team_name):
        try:
            return CTFTeam.objects.get(pk=team_name)
        except CTFTeam.DoesNotExist:
            return None


class Token_Backend(BaseBackend):
    def authenticate(self, request, token=None):
        try:
            team_token_obj = CTFTeam_LongtermTokens.objects.get(pk=token)
            return team_token_obj.team
        except CTFTeam_LongtermTokens.DoesNotExist:
            return None

    def get_user(self, team_name):
        try:
            return CTFTeam.objects.get(pk=team_name)
        except CTFTeam.DoesNotExist:
            return None

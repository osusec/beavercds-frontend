from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Exists, OuterRef, Count, Sum, Window, F, Case, When, Subquery, Min
from django.db.models.functions import Rank
from bctf.settings import THRESHOLD_SOLVES
from .mixins import AdminRequiredMixin
from chals.models import *
from account.models import *


# Create your views here.
class AdminHome (LoginRequiredMixin, AdminRequiredMixin, View):
    def get (self, request):
        return render (request, 'admin/home.html')

class AdminChals (LoginRequiredMixin, AdminRequiredMixin, View):
    def get (self, request):
        team = request.user

        chals = (Challenge.objects
            .filter(active=True)
            .annotate (solved=Exists(
                ChallengeSolve.objects
                .filter(challenge=OuterRef('pk'), team=team)
            ))
            .annotate (num_solves=Count('challengesolve'))
            .annotate (current_points_value=(
                ((F('min_points')-F('max_points'))*(F('num_solves')**2)/(THRESHOLD_SOLVES**2))+F('max_points')
            ))
            .annotate (current_points_value=Case(
                When(current_points_value__lte=F('min_points'), then=F('min_points')),
                default=F('current_points_value')
            ))
        )

        chals_with_files = [(chal, ChallengeFile.objects.filter(challenge=chal)) for chal in chals.order_by('solved')]

        return render (request, 'admin/chals.html', {'chals': chals_with_files})

class AdminSolves (LoginRequiredMixin, AdminRequiredMixin, View):
    def get (self, request):
        min_per_chal = Subquery(
            ChallengeSolve.objects
            .filter(challenge=OuterRef('challenge'))
            .order_by('time_of_solve')
            .values('time_of_solve')[:1]
        )

        firstbloods = (
            ChallengeSolve.objects
            .annotate(min_ts=min_per_chal)
            .filter(time_of_solve=F('min_ts'))
            .order_by('-time_of_solve')
            .values (
                challenge_name=F("challenge__name"),
                team_name=F("team__team_name"),
                solvetime=F("time_of_solve")
            )
        )

        number_solves = (
            Challenge.objects
            .annotate(solves=Count('challengesolve'))
            .values(
                challenge_name=F('name'),
                solves=F('solves')
            )
            .order_by('solves')
        )

        all_solves = (
            ChallengeSolve.objects
            .order_by('-time_of_solve')
            .values(
                team_name=F('team__team_name'),
                solvetime=F('time_of_solve'),
                challenge_name=F('challenge__name')
            )
        )

        return render (request, 'admin/solves.html', {'firstbloods': firstbloods[:5], 'number_solves': number_solves, 'all_solves': all_solves})
        
class AdminTeams (LoginRequiredMixin, AdminRequiredMixin, View):
    def get (self, request):
        # TODO: most disgusting code ever written
        solve_count_subq = (ChallengeSolve.objects
            .filter(challenge=OuterRef('challengesolve__challenge__pk'))
            .values('challenge')
            .annotate(num_solves=Count('challenge'))
            .values('num_solves')
        )

        score_entries = (CTFTeam.objects
            .annotate (sum_points=Sum(
                Case(
                    When(
                        challengesolve__challenge__min_points__lte=(
                            ((F('challengesolve__challenge__min_points')-F('challengesolve__challenge__max_points'))*(Subquery(solve_count_subq)**2)/(THRESHOLD_SOLVES**2))+F('challengesolve__challenge__max_points')
                        ),
                        then=(
                            ((F('challengesolve__challenge__min_points')-F('challengesolve__challenge__max_points'))*(Subquery(solve_count_subq)**2)/(THRESHOLD_SOLVES**2))+F('challengesolve__challenge__max_points')
                        )
                    ),
                    default=F('challengesolve__challenge__min_points')
                ),
                default=0
            ))
            .annotate(place=Window(
                expression=Rank(),
                order_by='-sum_points'
            ))
            .order_by('-sum_points')
        )

        teams_with_emails = [(team, CTFTeam_ContactEmails.objects.filter(team=team)) for team in score_entries]

        num_teams = CTFTeam.objects.all().count()

        return render (request, 'admin/teams.html', {'scores': score_entries.filter(place__lte=3), 'teams_with_emails': teams_with_emails, 'num_teams': num_teams})

# TODO: make sure only active challenges are being retrieved

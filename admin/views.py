from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count,
    F,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Window,
)
from django.db.models.functions import Greatest, Rank
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View

from account.models import *
from bctf.settings import THRESHOLD_SOLVES
from chals.models import *

from .forms import *
from .mixins import AdminRequiredMixin

# Create your views here.


class AdminChals(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        team = request.user

        chals = (
            Challenge.objects.filter(active=True)
            .annotate(
                num_solves=Count(
                    "challengesolve", filter=Q(challengesolve__team__is_active=True)
                )
            )
            .annotate(
                current_points_value=Greatest(
                    F("min_points"),
                    (
                        (F("min_points") - F("max_points"))
                        * (F("num_solves") ** 2)
                        / (THRESHOLD_SOLVES**2)
                    )
                    + F("max_points"),
                )
            )
        )

        chals_with_files = [
            (chal, ChallengeFile.objects.filter(challenge=chal))
            for chal in chals.order_by("num_solves")
        ]

        return render(request, "admin/chals.html", {"chals": chals_with_files})


class AdminSolves(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        solve_search = request.GET.get("search")

        min_per_chal = Subquery(
            ChallengeSolve.objects.filter(
                challenge=OuterRef("challenge"), team__is_active=True
            )
            .order_by("time_of_solve", "pk")
            .values("pk")[:1]
        )

        firstbloods = (
            ChallengeSolve.objects.annotate(min_ts=min_per_chal)
            .filter(pk=F("min_ts"))
            .order_by("-time_of_solve")
            .values(
                challenge_name=F("challenge__name"),
                team_name=F("team__team_name"),
                solvetime=F("time_of_solve"),
            )
        )

        number_solves = (
            Challenge.objects.annotate(
                solves=Count(
                    "challengesolve", filter=Q(challengesolve__team__is_active=True)
                )
            )
            .values(challenge_name=F("name"), solves=F("solves"))
            .order_by("solves")
        )

        all_solves = ChallengeSolve.objects.order_by("-time_of_solve")

        # TODO: bug, won't match against the Open bracket
        if solve_search:
            all_solves = all_solves.filter(
                Q(team__team_name__icontains=solve_search)
                | Q(team__bracket__bracket_name__icontains=solve_search)
                | Q(challenge__name__icontains=solve_search)
                | Q(challenge__category__icontains=solve_search)
            )

        return render(
            request,
            "admin/solves.html",
            {
                "firstbloods": firstbloods[:5],
                "number_solves": number_solves,
                "all_solves": all_solves,
                "solve_search": solve_search,
            },
        )


class AdminTeams(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):

        solve_count_subq = (
            ChallengeSolve.objects.filter(
                challenge=OuterRef("challengesolve__challenge__pk"),
                team__is_active=True,
            )
            .values("challenge")
            .annotate(num_solves=Count("challenge"))
            .values("num_solves")
        )

        score_entries = (
            CTFTeam.objects.filter(is_active=True)
            .annotate(
                sum_points=Sum(
                    Greatest(
                        F("challengesolve__challenge__min_points"),
                        (
                            (
                                F("challengesolve__challenge__min_points")
                                - F("challengesolve__challenge__max_points")
                            )
                            * (Subquery(solve_count_subq) ** 2)
                            / (THRESHOLD_SOLVES**2)
                        )
                        + F("challengesolve__challenge__max_points"),
                    ),
                    default=0,
                )
            )
            .annotate(place=Window(expression=Rank(), order_by="-sum_points"))
            .order_by("-sum_points")
        )

        teams_with_emails = [
            (team, CTFTeam_ContactEmails.objects.filter(team=team))
            for team in CTFTeam.objects.all().order_by("pk")
        ]

        num_teams = CTFTeam.objects.all().count()

        brackets = CTFTeam_Bracket.objects.all()

        return render(
            request,
            "admin/teams.html",
            {
                "scores": score_entries.filter(place__lte=10),
                "teams_with_emails": teams_with_emails,
                "num_teams": num_teams,
                "brackets": brackets,
            },
        )


# TODO: make sure only active challenges are being retrieved


class ChangeBracketAdm(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request):
        form = ChangeBracketAdmForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data["team"]
            bracket = form.cleaned_data["bracket"]

            team.bracket = bracket
            team.save()
            return JsonResponse({"redirect": reverse_lazy("admin-teams")})
        else:
            errors = []
            for field, err in form.errors.items():
                for inst in err:
                    errors.append(inst)
            return JsonResponse({"errors": errors}, status=400)


class DeactivateTeam(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request):
        self_team = request.user

        form = ActivateDeactivateTeamForm(request.POST)
        if form.is_valid():
            team_d = form.cleaned_data["team"]
            available_admins = CTFTeam.objects.filter(
                is_admin=True, is_active=True
            ).count()

            if team_d == self_team:
                return JsonResponse({"errors": ["Cannot deactivate self."]}, status=400)
            if available_admins <= 1:
                return JsonResponse(
                    {"errors": ["Cannot deactivate the last remaining admin."]},
                    status=400,
                )

            team_d.is_active = False
            team_d.save()
            return JsonResponse({"redirect": reverse_lazy("admin-teams")})
        else:
            return JsonResponse({"errors": ["Team not found."]}, status=404)


class ActivateTeam(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request):
        self_team = request.user

        form = ActivateDeactivateTeamForm(request.POST)
        if form.is_valid():
            team_a = form.cleaned_data["team"]

            if team_a == self_team:
                return JsonResponse({"errors": ["Cannot activate self."]}, status=400)
            else:
                team_a.is_active = True
                team_a.save()
                return JsonResponse({"redirect": reverse_lazy("admin-teams")})
        else:
            return JsonResponse({"errors": ["Team not found."]}, status=404)

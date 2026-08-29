from django.shortcuts import render
from chals.models import *
from account.models import *
from django.db.models import (
    Exists,
    OuterRef,
    Count,
    Sum,
    Window,
    F,
    Case,
    When,
    Subquery,
    Min,
)
from django.db.models.functions import Rank, Greatest
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    JsonResponse,
)
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views import View
import json
from bctf.settings import THRESHOLD_SOLVES
from chals.mixins import CTFStartMixin


class FrontPage(View):
    def get(self, request):
        return render(request, "index.html")


class Scores(CTFStartMixin, View):
    def get(self, request):
        # bracket name, which is unique
        bracket = request.GET.get("bracket")

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

        if bracket:
            score_entries = score_entries.filter(bracket__bracket_name=bracket)
        elif bracket == "":
            score_entries = score_entries.filter(bracket=None)

        brackets = CTFTeam_Bracket.objects.distinct("bracket_name")

        return render(
            request, "scoreboard.html", {"scores": score_entries, "brackets": brackets}
        )


# For CTFTime
class ScoresFeed(CTFStartMixin, View):
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

        score_entries = score_entries.values(
            pos=F("place"), team=F("team_name"), score=F("sum_points")
        )

        return JsonResponse({"standings": list(score_entries)})


class Rules(View):
    def get(self, request):
        return render(request, "rules.html", {})

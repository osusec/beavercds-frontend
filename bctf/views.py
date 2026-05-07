import json

from django.db import transaction
from django.db.models import (
    Case,
    Count,
    Exists,
    F,
    OuterRef,
    Subquery,
    Sum,
    When,
    Window,
)
from django.db.models.functions import Rank
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    JsonResponse,
)
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from account.models import *
from bctf.settings import THRESHOLD_SOLVES
from chals.mixins import CTFStartMixin
from chals.models import *


class FrontPage(View):
    def get(self, request):
        return render(request, "index.html")


class Scores(CTFStartMixin, View):
    def get(self, request):
        # TODO: most disgusting code ever written
        solve_count_subq = (
            ChallengeSolve.objects.filter(
                challenge=OuterRef("challengesolve__challenge__pk")
            )
            .values("challenge")
            .annotate(num_solves=Count("challenge"))
            .values("num_solves")
        )

        score_entries = (
            CTFTeam.objects.annotate(
                sum_points=Sum(
                    Case(
                        When(
                            challengesolve__challenge__min_points__lte=(
                                (
                                    (
                                        F("challengesolve__challenge__min_points")
                                        - F("challengesolve__challenge__max_points")
                                    )
                                    * (Subquery(solve_count_subq) ** 2)
                                    / (THRESHOLD_SOLVES**2)
                                )
                                + F("challengesolve__challenge__max_points")
                            ),
                            then=(
                                (
                                    (
                                        F("challengesolve__challenge__min_points")
                                        - F("challengesolve__challenge__max_points")
                                    )
                                    * (Subquery(solve_count_subq) ** 2)
                                    / (THRESHOLD_SOLVES**2)
                                )
                                + F("challengesolve__challenge__max_points")
                            ),
                        ),
                        default=F("challengesolve__challenge__min_points"),
                    ),
                    default=0,
                )
            )
            .annotate(place=Window(expression=Rank(), order_by="-sum_points"))
            .order_by("-sum_points")
        )

        return render(request, "scoreboard.html", {"scores": score_entries})


# For CTFTime
class ScoresFeed(CTFStartMixin, View):
    def get(self, request):
        # TODO: most disgusting code ever written
        solve_count_subq = (
            ChallengeSolve.objects.filter(
                challenge=OuterRef("challengesolve__challenge__pk")
            )
            .values("challenge")
            .annotate(num_solves=Count("challenge"))
            .values("num_solves")
        )

        score_entries = (
            CTFTeam.objects.annotate(
                sum_points=Sum(
                    Case(
                        When(
                            challengesolve__challenge__min_points__lte=(
                                (
                                    (
                                        F("challengesolve__challenge__min_points")
                                        - F("challengesolve__challenge__max_points")
                                    )
                                    * (Subquery(solve_count_subq) ** 2)
                                    / (THRESHOLD_SOLVES**2)
                                )
                                + F("challengesolve__challenge__max_points")
                            ),
                            then=(
                                (
                                    (
                                        F("challengesolve__challenge__min_points")
                                        - F("challengesolve__challenge__max_points")
                                    )
                                    * (Subquery(solve_count_subq) ** 2)
                                    / (THRESHOLD_SOLVES**2)
                                )
                                + F("challengesolve__challenge__max_points")
                            ),
                        ),
                        default=F("challengesolve__challenge__min_points"),
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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, Exists, F, Max, OuterRef, When
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from bctf.settings import THRESHOLD_SOLVES

from .forms import SubmitFlagForm
from .mixins import CTFEndMixin, CTFStartMixin
from .models import *


class ListChal(LoginRequiredMixin, CTFStartMixin, View):
    def get(self, request):
        team = request.user
        category = request.GET.get("category")

        # TODO: most disgusting code ever written
        chals = (
            Challenge.objects.filter(active=True)
            .annotate(
                solved=Exists(
                    ChallengeSolve.objects.filter(challenge=OuterRef("pk"), team=team)
                )
            )
            .annotate(num_solves=Count("challengesolve"))
            .annotate(
                current_points_value=(
                    (
                        (F("min_points") - F("max_points"))
                        * (F("num_solves") ** 2)
                        / (THRESHOLD_SOLVES**2)
                    )
                    + F("max_points")
                )
            )
            .annotate(
                current_points_value=Case(
                    When(
                        current_points_value__lte=F("min_points"), then=F("min_points")
                    ),
                    default=F("current_points_value"),
                )
            )
        )

        if category:
            chals = chals.filter(category=category)

        chals_with_files = [
            (chal, ChallengeFile.objects.filter(challenge=chal))
            for chal in chals.order_by("solved")
        ]

        categories = Challenge.objects.distinct("category")

        return render(
            request,
            "challenges.html",
            {
                "chals": chals_with_files,
                "categories": categories,
                "submit_form": SubmitFlagForm,
            },
        )


class SubmitFlag(CTFStartMixin, LoginRequiredMixin, CTFEndMixin, View):
    def post(self, request):
        team = request.user

        form = SubmitFlagForm(request.POST)
        if form.is_valid():
            challenge = form.cleaned_data["challenge"]
            submitted_flag = form.cleaned_data["submitted_flag"]

            if ChallengeSolve.objects.filter(challenge=challenge, team=team).exists():
                # Team has already submitted this flag before
                return JsonResponse({"redirect": reverse_lazy("chals-list")})

            if submitted_flag == challenge.flag:
                new_solve = ChallengeSolve(challenge=challenge, team=team)
                new_solve.save()
                return JsonResponse({"redirect": reverse_lazy("chals-list")})
            else:
                return JsonResponse({"errors": ["Flag was incorrect."]}, status=400)

        else:  # Error with form, probably challenge not found
            return JsonResponse({"errors": ["Challenge not found."]}, status=404)

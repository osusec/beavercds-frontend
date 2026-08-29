import json

from django.contrib.auth.hashers import check_password, make_password
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
from chals.models import *


class CheckAccess(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})


class ResolveState(View):
    def post(self, request):
        try:
            new_json_state = json.loads(request.body.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            return JsonResponse("Missing or bad JSON provided.", status=400)
        # Check that all ids are unique and that all fields are present
        # If not, fail early
        if not _check_unique_ids(new_json_state):
            return JsonResponse("Duplicate IDs present.", status=400)
        if not _check_complete_chal_fields(new_json_state):
            return JsonResponse("Missing required fields.", status=400)

        result_state = []
        removed_state = []

        # Begin changing state
        with transaction.atomic():
            # Lock the ChallengeSolve table
            for i in ChallengeSolve.objects.select_for_update().all():
                break

            # Set all current state to inactive.
            # Requisite challenges will be reactivated when we loop over the new state.
            # Challenges that were deployed but no longer, will remain inactive.
            for chal in Challenge.objects.all():
                chal.active = False
                chal.save()

            # Loop over new state, implement
            for new_state in new_json_state:
                chal_id = new_state["id"]
                try:
                    # Update object
                    chal = Challenge.objects.get(pk=chal_id)
                    chal.name = new_state["name"]
                    chal.author = new_state["author"]
                    chal.category = new_state["category"]
                    chal.description = new_state["description"]
                    chal.min_points = new_state["min_points"]
                    chal.max_points = new_state["max_points"]
                    chal.flag = new_state["flag"]
                    chal.active = True
                    chal.save()

                    chal_files = ChallengeFile.objects.filter(challenge=chal).delete()
                    for file in new_state["files"]:
                        chal_file = ChallengeFile(
                            challenge=chal, url=file, basename=file.split("/")[-1]
                        )
                        chal_file.save()
                    result_state.append(chal_id)

                except Challenge.DoesNotExist:
                    # Create new object
                    chal = Challenge(
                        chal_id=chal_id,
                        name=new_state["name"],
                        author=new_state["author"],
                        category=new_state["category"],
                        description=new_state["description"],
                        min_points=new_state["min_points"],
                        max_points=new_state["max_points"],
                        flag=new_state["flag"],
                        active=True,
                    )
                    chal.save()
                    for file in new_state["files"]:
                        chal_file = ChallengeFile(
                            challenge=chal,
                            url=file,
                            # TODO: brittle
                            basename=file.split("/")[-1],
                        )
                        chal_file.save()
                    result_state.append(chal_id)

            # Delete challenges that are inactive and *have no solves*
            for chal in Challenge.objects.filter(active=False):
                chal_id = chal.chal_id
                solves = ChallengeSolve.objects.filter(challenge=chal)
                if solves.count() == 0:
                    chal.delete()
                # else: leave inactive
                removed_state.append(chal_id)
        # end: with transaction.atomic()

        return JsonResponse({"current": result_state, "removed": removed_state})


class UpdateBrackets(View):
    # This function is a lot less heavy than ResolveState because it is
    #  assumed that there are a lot less brackets than challenges and
    #  that brackets will change much less frequently than challenges
    def post(self, request):
        try:
            new_json_state = json.loads(request.body.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            return JsonResponse("Missing or bad JSON provided.", status=400)

        if not _check_unique_brackets(new_json_state):
            return JsonResponse("Duplicate bracket names present.", status=400)
        if not _check_complete_bracket_fields(new_json_state):
            return JsonResponse("Missing required fields.", status=400)

        result_state = []
        current_state = set(
            CTFTeam_Bracket.objects.values_list("bracket_name", flat=True)
        )

        # Begin changing state
        with transaction.atomic():
            for bracket_json in new_json_state:
                bracket_name = bracket_json["name"]
                open_bracket = False if bracket_json["password"] else True
                access_hash = (
                    None if open_bracket else make_password(bracket_json["password"])
                )

                if bracket_name in current_state:
                    # Currently existing bracket
                    (
                        CTFTeam_Bracket.objects.filter(
                            bracket_name=bracket_name
                        ).update(open_bracket=open_bracket, access_hash=access_hash)
                    )
                    current_state.remove(bracket_name)
                else:
                    # New bracket
                    new_bracket = CTFTeam_Bracket(
                        bracket_name=bracket_name,
                        open_bracket=open_bracket,
                        access_hash=access_hash,
                    )
                    new_bracket.save()
                result_state.append(bracket_name)

            # Lock the users table to edit brackets
            for i in CTFTeam.objects.select_for_update().all():
                break

            # Remove what's left
            for old_bracket in current_state:
                # Remove teams from the bracket if need be
                # This places them in the default Open bracket
                (
                    CTFTeam.objects.filter(bracket__bracket_name=old_bracket).update(
                        bracket=None
                    )
                )
                # Delete the bracket
                (CTFTeam_Bracket.objects.filter(bracket_name=old_bracket).delete())
        # end: with transaction.atomic()

        return JsonResponse({"current": result_state, "removed": list(current_state)})


def _check_unique_ids(new_chal_state):
    # Check that all ids are unique
    new_ids = set()
    for c in new_chal_state:
        if c["id"] in new_ids:
            # Duplicate id detected, fail
            return False
        new_ids.add(c["id"])
    return True


def _check_complete_chal_fields(new_chal_state):
    for c in new_chal_state:
        if (
            (not "id" in c)
            or (not "name" in c)
            or (not "author" in c)
            or (not "category" in c)
            or (not "description" in c)
            or (not "min_points" in c)
            or (not "max_points" in c)
            or (not "flag" in c)
        ):
            # Missing required fields, fail
            return False
    return True


def _check_unique_brackets(new_bracket_state):
    # Check that all names are unique
    new_names = set()
    for b in new_bracket_state:
        if b["name"] in new_names:
            # Duplicate name detected, fail
            return False
        new_names.add(b["name"])
    return True


def _check_complete_bracket_fields(new_bracket_state):
    for b in new_bracket_state:
        if (not "name" in b) or (not "password" in b):
            # Missing required fields, fail
            return False
    return True

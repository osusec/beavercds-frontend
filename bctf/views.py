from django.shortcuts import render
from chals.models import Challenge, ChallengeFile, ChallengeSolve
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views import View
import json


def FrontPage (request):
    return render (request, "index.html", {'the': 'Hewwo'})

def Scores (request):
    pass 


# API endpoints below

def CheckAccess (request):
    response_obj = {"status":"ok"}
    if request.user.is_authenticated:
        response_obj["user"] = request.user.get_username()
    return HttpResponse(json.dumps(response_obj))


class ResolveState(View):
    def post (self, request):
        try:
            new_json_state = json.loads(request.body.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest("Missing or bad JSON provided.")
        # Check that all ids are unique and that all fields are present
        # If not, fail early
        if not _check_unique_ids(new_json_state):
            return HttpResponseBadRequest("Duplicate IDs present.")
        if not _check_complete_fields(new_json_state):
            return HttpResponseBadRequest("Missing required fields.")

        result_state = []
        removed_state = []

        # Begin changing state
        with transaction.atomic():
            # Set all current state to inactive.
            # Requisite challenges will be reactivated when we loop over the new state.
            # Challenges that were deployed but no longer, will remain inactive.
            for chal in Challenge.objects.all():
                chal.active = False
                chal.save()

            # Loop over new state, implement
            for new_state in new_json_state:
                chal_id = new_state['id']
                try:
                    # Update object
                    chal = Challenge.objects.get(pk=chal_id)
                    chal.name = new_state['name']
                    chal.author = new_state['author']
                    chal.category = new_state['category']
                    chal.description = new_state['description']
                    chal.min_points = new_state['min_points']
                    chal.max_points = new_state['max_points']
                    chal.flag = new_state['flag']
                    chal.active = True
                    chal.save()

                    chal_files = ChallengeFile.objects.filter(challenge=chal).delete()
                    for file in new_state['files']:
                        chal_file = ChallengeFile(
                            challenge=chal,
                            url=file,
                            basename=file.split('/')[-1]
                        )
                        chal_file.save()
                    result_state.append(chal_id)

                except Challenge.DoesNotExist:
                    # Create new object
                    chal = Challenge(
                        chal_id= chal_id,
                        name = new_state['name'],
                        author = new_state['author'],
                        category = new_state['category'],
                        description = new_state['description'],
                        min_points = new_state['min_points'],
                        max_points = new_state['max_points'],
                        flag = new_state['flag'],
                        active = True
                    )
                    chal.save()
                    for file in new_state['files']:
                        chal_file = ChallengeFile(
                            challenge=chal,
                            url=file,
                            basename=file.split('/')[-1]
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

    # def get (self, request):
    #     pass # TODO: This is for giving the CSRF token


def _check_unique_ids (new_chal_state):
    # Check that all ids are unique
    new_ids = set()
    for c in new_chal_state:
        if c['id'] in new_ids:
            # Duplicate id detected, fail
            return False
        new_ids.add(c['id'])
    return True

def _check_complete_fields (new_chal_state):
    for c in new_chal_state:
        if ((not "id" in c) or 
        (not "name" in c) or
        (not "author" in c)  or
        (not "category" in c)  or
        (not "description" in c)  or
        (not "min_points" in c) or
        (not "max_points" in c)  or
        (not "flag" in c)):
            # Missing required fields, fail
            return False
    return True


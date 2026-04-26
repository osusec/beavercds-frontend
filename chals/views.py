from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.db.models import Exists, OuterRef
from .forms import SubmitFlagForm
from django.urls import reverse_lazy

class ListChal (LoginRequiredMixin, View):
    def get (self, request):
        team = request.user
        category = request.GET.get('category')

        chals = (Challenge.objects
            .filter(active=True)
            .annotate (solved=Exists(
                ChallengeSolve.objects
                .filter(challenge=OuterRef('pk'), team=team)
            ))
        )
        if category:
            chals = chals.filter(category=category)

        categories = Challenge.objects.distinct('category')

        return render (request, "challenges.html", {'chals': chals.order_by('solved'), 'categories': categories, 'submit_form': SubmitFlagForm})

class SubmitFlag (LoginRequiredMixin, View):
    def post (self, request):
        team = request.user

        form = SubmitFlagForm(request.POST)
        if form.is_valid():
            challenge = form.cleaned_data['challenge']
            submitted_flag = form.cleaned_data['submitted_flag']

            if not ChallengeSolve.objects.filter(challenge=challenge, team=team).exists():
                if submitted_flag == challenge.flag:
                    new_solve = ChallengeSolve (challenge=challenge, team=team)
                    new_solve.save()
        
        # TODO: once i can figure out how to print errors, do rendering instead
        return redirect(reverse_lazy('chals-list'))
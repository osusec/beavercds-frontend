from account.models import *
from chals.models import *
from django import forms


class ChangeBracketAdmForm(forms.Form):
    team = forms.ModelChoiceField(queryset=CTFTeam.objects.all())
    bracket = forms.ModelChoiceField(
        queryset=CTFTeam_Bracket.objects.all(), required=False, empty_label="Open"
    )


class ActivateDeactivateTeamForm(forms.Form):
    # Not worrying about redundant activations/deactivations
    team = forms.ModelChoiceField(queryset=CTFTeam.objects.all())

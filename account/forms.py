from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms

class TeamCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CTFTeam
        fields = ("team_name",) # password fields included

    def save (self, commit=True):
        team = super().save(commit=False)
        team.ctftime_bool = False
        if commit:
            team.save()
        return team


class TokenDeleteForm(forms.Form):
    token = forms.ModelChoiceField(queryset=CTFTeam_LongtermTokens.objects.none())

    # TODO: double check that this is sufficient authz
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['token'].queryset = CTFTeam_LongtermTokens.objects.filter(team=user)


class AddContactEmailForm (forms.Form):
    email = forms.EmailField(label="Contact Email")


class RemoveContactEmailForm (forms.Form):
    email = forms.ModelChoiceField (queryset=CTFTeam_ContactEmails.objects.none())

    # TODO: double check that this is sufficient authz
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].queryset = CTFTeam_ContactEmails.objects.filter(team=user)

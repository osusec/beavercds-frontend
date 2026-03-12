from django.contrib.auth.forms import UserCreationForm
from .models import CTFTeam

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

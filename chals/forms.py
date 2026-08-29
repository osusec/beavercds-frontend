from django import forms

from .models import Challenge


class SubmitFlagForm(forms.Form):
    challenge = forms.ModelChoiceField(queryset=Challenge.objects.filter(active=True))
    submitted_flag = forms.CharField(label="Flag", max_length=1000)

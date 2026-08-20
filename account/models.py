from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from .managers import CTFTeamManager

from bctf.settings import TOKEN_LENGTH

# Create your models here.

class CTFTeam_Bracket (models.Model):
    bracket_name = models.CharField(unique=True, max_length=200)
    open_bracket = models.BooleanField(default=True)
    access_hash = models.CharField(max_length=128, null=True)
    # 128 is chosen because thats what django's auth helper code sets
    # this field being null means it is an open bracket


class CTFTeam (AbstractBaseUser, PermissionsMixin):
    # TODO: no delineation between CTFTime and traditional logins
    # Team name = 128 characters to match CTFTime
    team_name = models.CharField (primary_key=True, max_length=128)
    ctftime_bool = models.BooleanField()
    bracket = models.ForeignKey(CTFTeam_Bracket, on_delete=models.PROTECT, null=True)
    username = None
    is_admin = models.BooleanField(default=False) # TODO

    USERNAME_FIELD = 'team_name'
    REQUIRED_FIELDS = []

    objects = CTFTeamManager()

    def __str__(self):
        return self.team_name


class CTFTeam_ContactEmails (models.Model):
    team = models.ForeignKey(CTFTeam, on_delete=models.CASCADE)
    email = models.TextField()

class CTFTime_Team (models.Model):
    ctftime_id = models.IntegerField (primary_key=True)
    team = models.ForeignKey(CTFTeam, on_delete=models.CASCADE)

class CTFTeam_LongtermTokens (models.Model):
    team = models.ForeignKey(CTFTeam, on_delete=models.CASCADE)
    token = models.CharField(primary_key=True, max_length=2*TOKEN_LENGTH) # Base64
